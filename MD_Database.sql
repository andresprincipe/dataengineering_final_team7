-- =========================================================
-- Database: FinalProject
-- =========================================================

DROP DATABASE IF EXISTS "FinalProject";
CREATE DATABASE "FinalProject"
    WITH
    OWNER = jhu
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

-- =========================================================
-- Create schema
-- =========================================================
CREATE SCHEMA IF NOT EXISTS MD_data;

-- =========================================================
-- 1. Counties in MD
-- =========================================================
DROP TABLE IF EXISTS MD_data.Counties CASCADE;
CREATE TABLE MD_data.Counties (
    County_ID INT PRIMARY KEY,
    County_Name VARCHAR(50) NOT NULL,
    State CHAR(2) NOT NULL
);

-- =========================================================
-- 2. Average Wage Maryland
-- =========================================================
DROP TABLE IF EXISTS MD_data.AverageWageMaryland CASCADE;
CREATE TABLE MD_data.AverageWageMaryland (
    Year INT PRIMARY KEY,
    WageThatYear INT NOT NULL,
    DateCreated VARCHAR(50)
);

-- =========================================================
-- 3. Average Wage per County
-- =========================================================
DROP TABLE IF EXISTS MD_data.AverageWagePerCounty CASCADE;
CREATE TABLE MD_data.AverageWagePerCounty (
    WageForCounty INT PRIMARY KEY,
    Year INT NOT NULL,
    County_ID INT NOT NULL,
    FOREIGN KEY (Year) REFERENCES MD_data.AverageWageMaryland(Year),
    FOREIGN KEY (County_ID) REFERENCES MD_data.Counties(County_ID)
);

-- =========================================================
-- 4. Air Enforcements in MD
-- =========================================================
DROP TABLE IF EXISTS MD_data.AirEnforcementsInMD CASCADE;
CREATE TABLE MD_data.AirEnforcementsInMD (
    Ai_Combined VARCHAR(50) PRIMARY KEY,
    AchievedDate VARCHAR(50),
    ActionDescription VARCHAR(50),
    Address VARCHAR(50),
    City VARCHAR(50),
    ZipCode INT,
    County_ID INT,
    Documents VARCHAR(50),
    FOREIGN KEY (County_ID) REFERENCES MD_data.Counties(County_ID)
);

-- =========================================================
-- 5. Water Enforcements in MD
-- =========================================================
DROP TABLE IF EXISTS MD_data.WaterEnforcementsInMD CASCADE;
CREATE TABLE MD_data.WaterEnforcementsInMD (
    Ai_Combined VARCHAR(50) PRIMARY KEY,
    Upload_ID VARCHAR(50),
    Address VARCHAR(50),
    City VARCHAR(50),
    Program VARCHAR(50),
    EnforcementAction VARCHAR(50),
    EnforcementNumber VARCHAR(50),
    ZipCode INT,
    County_ID INT,
    EnforcementActionIssued VARCHAR(50),
    CaseClosed VARCHAR(50),
    Media VARCHAR(50),
    FOREIGN KEY (County_ID) REFERENCES MD_data.Counties(County_ID)
);
