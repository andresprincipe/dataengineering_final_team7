
-- Create schema
CREATE SCHEMA IF NOT EXISTS md_data;


-- 1. counties
DROP TABLE IF EXISTS md_data.counties CASCADE;
CREATE TABLE md_data.counties (
    county_id INT PRIMARY KEY,
    county_name VARCHAR(50) NOT NULL,
    state CHAR(50) NOT NULL
);


-- 2. average_wage_maryland
DROP TABLE IF EXISTS md_data.average_wage_maryland CASCADE;
CREATE TABLE md_data.average_wage_maryland (
    year INT PRIMARY KEY,
    wage_that_year INT NOT NULL,
    date_created VARCHAR(50)
);

-- 3. average_wage_per_county
DROP TABLE IF EXISTS md_data.average_wage_per_county CASCADE;
CREATE TABLE md_data.average_wage_per_county (
    wage_for_county INT PRIMARY KEY,
    year INT NOT NULL,
    county_id INT NOT NULL,
    FOREIGN KEY (year) REFERENCES md_data.average_wage_maryland(year),
    FOREIGN KEY (county_id) REFERENCES md_data.counties(county_id)
);


-- 4. air_enforcements_in_md
DROP TABLE IF EXISTS md_data.air_enforcements_in_md CASCADE;
CREATE TABLE md_data.air_enforcements_in_md (
    ai_combined VARCHAR(255) PRIMARY KEY,
    achieved_date VARCHAR(255),
    action_description VARCHAR(255),
    address VARCHAR(255),
    city VARCHAR(50),
    zip_code INT,
    county_id INT,
    documents VARCHAR(255),
    FOREIGN KEY (county_id) REFERENCES md_data.counties(county_id)
);

-- 5. water_enforcements_in_md
DROP TABLE IF EXISTS md_data.water_enforcements_in_md CASCADE;
CREATE TABLE md_data.water_enforcements_in_md (
    ai_combined VARCHAR(255) PRIMARY KEY,
    upload_id VARCHAR(255),
    address VARCHAR(255),
    city VARCHAR(255),
    program VARCHAR(255),
    enforcement_action VARCHAR(255),
    enforcement_number VARCHAR(255),
    zip_code INT,
    county_id INT,
    enforcement_action_issued VARCHAR(255),
    case_closed VARCHAR(255),
    media VARCHAR(255),
    FOREIGN KEY (county_id) REFERENCES md_data.counties(county_id)
);
