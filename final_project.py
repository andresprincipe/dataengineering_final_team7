import psycopg2
import pandas as pd

# Connect to PostgreSQL (host=localhost since you're running Python on your Mac)
conn = psycopg2.connect(
    host="localhost",            # not container name; use localhost
    port="5432",
    database="final_project",    # all lowercase to match your created DB
    user="jhu",
    password="jhu123"
)
cur = conn.cursor()
print("Connected to final_project database!")

# Load CSVs
air_df = pd.read_csv("clean_data/md_air_enforcement_cleaned.csv")
water_df = pd.read_csv("clean_data/md_water_enforcement_cleaned.csv")
wage_df = pd.read_csv("clean_data/Maryland_Average_Wage_Per_Job_(Current_Dollars)__2014-2024_cleaned.csv")

# 1. Counties table
counties = pd.concat([air_df["county"], water_df["county"]]).dropna().unique().tolist()

maryland_index = wage_df.columns.get_loc("MARYLAND")
wage_counties = [
    col.replace("County", "").strip()
    for col in wage_df.columns[maryland_index + 1 : -1]
]

all_counties = list(set(counties + wage_counties))
counties_df = pd.DataFrame({"county_name": all_counties})
counties_df["county_id"] = range(1, len(counties_df) + 1)
counties_df["state"] = counties_df["county_name"].apply(
    lambda x: "N/A" if "Outside of Maryland" in x else "MD"
)

for _, row in counties_df.iterrows():
    cur.execute("""
        INSERT INTO md_data.counties (county_id, county_name, state)
        VALUES (%s, %s, %s)
        ON CONFLICT (county_id) DO NOTHING;
    """, (row["county_id"], row["county_name"], row["state"]))

conn.commit()

# Normalize county names for consistent matching
def normalize_county(name):
    if pd.isnull(name):
        return None
    name = name.strip().lower().replace("county", "").replace("city", "").strip()
    return name

counties_df["normalized_name"] = counties_df["county_name"].apply(normalize_county)
county_map = dict(zip(counties_df["normalized_name"], counties_df["county_id"]))

# 2. Air enforcements table
for _, row in air_df.iterrows():
    cur.execute("""
        INSERT INTO md_data.air_enforcements_in_md
        (ai_combined, achieved_date, action_description, address, city,
         zip_code, county_id, documents)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ai_combined) DO NOTHING;
    """, (
        row["ai_combined"],
        row.get("achieved_date"),
        row.get("action_description"),
        row.get("addressinfo"),
        row.get("city"),
        row.get("zip"),
        county_map.get(normalize_county(row["county"])),
        row.get("documents")
    ))
conn.commit()

# 3. Water enforcements table
for _, row in water_df.iterrows():
    cur.execute("""
        INSERT INTO md_data.water_enforcements_in_md
        (ai_combined, upload_id, address, city, program,
         enforcement_action, enforcement_number, zip_code, county_id,
         enforcement_action_issued, case_closed, media)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ai_combined) DO NOTHING;
    """, (
        row["ai_combined"],
        row.get("upload_id"),
        row.get("address"),
        row.get("city"),
        row.get("program"),
        row.get("enforcement_action"),
        row.get("enforcement_action_no"),
        row.get("zip"),
        county_map.get(row.get("county")),
        row.get("enforcement_action_issued"),
        row.get("case_closed"),
        row.get("media")
    ))
conn.commit()

# 4. Average wage Maryland table
wage_maryland = wage_df[["Year", "MARYLAND", "Date created"]].copy()
wage_maryland.rename(columns={
    "Year": "year",
    "MARYLAND": "wage_that_year",
    "Date created": "date_created"
}, inplace=True)

for _, row in wage_maryland.iterrows():
    # Clean numeric wage (remove commas, convert to int safely)
    wage_value = row["wage_that_year"]
    if pd.notnull(wage_value):
        wage_value = int(str(wage_value).replace(",", "").strip())
    else:
        wage_value = None

    cur.execute("""
        INSERT INTO md_data.average_wage_maryland (year, wage_that_year, date_created)
        VALUES (%s, %s, %s)
        ON CONFLICT (year) DO NOTHING;
    """, (row["year"], wage_value, row["date_created"]))



# 5. Average wage per county table

county_cols = [c for c in wage_df.columns if "County" in c and c != "MARYLAND"]

melted = wage_df.melt(
    id_vars=["Year"],
    value_vars=county_cols,
    var_name="County_Name",
    value_name="WageForCounty"
)

# rename columns right after melting
melted.rename(columns={
    "Year": "year",
    "County_Name": "county_name",
    "WageForCounty": "wage_for_county"
}, inplace=True)

# clean and insert
for _, row in melted.iterrows():
    wage_val = row["wage_for_county"]
    if pd.notnull(wage_val):
        wage_val = int(str(wage_val).replace(",", "").strip())
    else:
        wage_val = None

    county_id = county_map.get(normalize_county(row["county_name"]))
    if county_id is None:
        continue  # skip rows with unmatched counties

    cur.execute("""
        INSERT INTO md_data.average_wage_per_county (wage_for_county, year, county_id)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING;
    """, (wage_val, row["year"], county_id))

conn.commit()

# Clean up
cur.close()
conn.close()
print("All CSV data successfully loaded into final_project database.")