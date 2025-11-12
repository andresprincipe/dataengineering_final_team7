# dataengineering_final_team7
Code necessary for building Johns Hopkins Data Engineering course final group project (Fall 2025). Main data source is found at https://opendata.maryland.gov/

## Data Set 1: Air & Radiation Enforcement Actions
- Under the “Environment” category on Maryland’s open data website, there are “enforcement actions” taken by the state of MD to those who violate air and safety regulations. This data gets updated daily and has an API. It contains details about the different sites (companies) and what actions were taken against them for violating air regulations. It also includes county data that can be combined with the other datasets.
  - Sample can be viewed here: [Maryland Department of the Environment - Air and Radiation Administration (ARA) Enforcement Actions](https://opendata.maryland.gov/Energy-and-Environment/Maryland-Department-of-the-Environment-Air-and-Rad/fpps-g5hi/data_preview)
  - API [endpoint](https://opendata.maryland.gov/resource/fpps-g5hi.json)

## Data Set 2: Wage Per Job
- The selected dataset “Maryland Average Wage Per Job (in Constant 2024 Dollars): 2014-2024”, provides economic data related to employment across Maryland’s counties. This is a batch CSV data set, sourced from Maryland Open Data Portal, contains annual information on the average wage per job in the last ten years. This dataset is organized by county and includes columns such as Year, County, and Average Wage (Current Dollars). It allows for analysis of wage trends across different regions in Maryland. This dataset can be combined with other Maryland datasets such as environmental data to explore how environmental or economic patterns may correlate throughout the state. I intend to join this data with other Maryland data based on counties in Maryland.
  - Sample can be viewed here: [Maryland Average Wage Per Job (Current Dollars): 2014-2024](https://opendata.maryland.gov/Demographic/Maryland-Average-Wage-Per-Job-Current-Dollars-2014/mk5a-nf44/data_preview)
  - Static CSV that is stored in repository

## Data Set 3: Wage Per Job
- The selected dataset “Maryland Average Wage Per Job (in Constant 2024 Dollars): 2014-2024”, provides economic data related to employment across Maryland’s counties. This is a batch CSV data set, sourced from Maryland Open Data Portal, contains annual information on the average wage per job in the last ten years. This dataset is organized by county and includes columns such as Year, County, and Average Wage (Current Dollars). It allows for analysis of wage trends across different regions in Maryland. This dataset can be combined with other Maryland datasets such as environmental data to explore how environmental or economic patterns may correlate throughout the state. I intend to join this data with other Maryland data based on counties in Maryland.
  - Sample can be viewed here: [Maryland Department of the Environment - Water and Science Administration (WSA) Enforcement Actions](https://opendata.maryland.gov/Energy-and-Environment/Maryland-Department-of-the-Environment-Water-and-S/qbwh-5vec/data_preview)
  - API [endpoint](https://opendata.maryland.gov/resource/qbwh-5vec.json)

# File/Directory Descriptions
- `fetchdata.py` is meant to be an initial script that retrieves data from APIs then processes them into cleaned CSV files that can be uploaded into a database.
- `mdprocessingutils.py` is a module that contains helper functions for processing parts of the Maryland API data before it is ingested into a database.
- `raw_data/` is a intermediate directory used by `fetchdata.py` to store data retrieved from GET requests in their native JSON format.
- `clean_data/` is a directory used by `fetchdata.py` to store processed versions of the data found in `raw_data/`. The data in this directory is in CSV format for the purposes of ingestion into a database.
- `MD_Database.sql` is the creating of the sql database that the cleaned csv files will be uploaded to.

# API Service Directories
- `api/` contains the FastAPI service used to query the PostgreSQL database and expose Maryland data through REST endpoints.
- `api/app/` is the main application package for the FastAPI service.
- `api/app/routers/` contains individual route files (e.g., `counties.py`, `wages.py`, `enforcements.py`, `health.py`) that define GET endpoints for each dataset.
- `api/app/reports/` stores summary or combined report logic used by the API.
- `api/app/db.py` includes database connection utilities (SQLAlchemy engine and session creation).
- `api/app/deps.py` provides shared dependencies for the API, including database session injection.
- `api/app/schemas.py` defines Pydantic models representing the expected structure of API responses based on the finalized table schemas.
- `api/Dockerfile` defines how the FastAPI container is built.
- `docker-compose.api.snippet.yml` contains the API service configuration for docker-compose, linking the API to PostgreSQL and Airflow within a shared network.
- `dags/` contains Airflow DAGs used for automated data extraction, transformation, and refresh pipelines.

# Instructions
- Download the docker .yml file to a designated folder.
- Go into your computers terminal, and change directories to that folder to run your .yml file
- Once in the folder with .yml folder run "docker-compose -f docker-compose.api.snippet.yml up -d"
- open Pgadmin and connect to the server from the container
- Run the sql script to initalize the database
- Run python script to input data into databse
... add Docker install instructions with appropriate commands ...

... add any aditional set up instructions ...

