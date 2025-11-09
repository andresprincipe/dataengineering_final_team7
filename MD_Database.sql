-- Database: FinalProject

-- DROP DATABASE IF EXISTS "FinalProject";

CREATE DATABASE "FinalProject"
    WITH
    OWNER = jhu
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

-- Creating schema 
CREATE SCHEMA MD_data

-- Creating tables
DROP TABLE IF EXISTS MD_data.WaterEnforcementsInMD;
CREATE TABLE MD_data.WaterEnforcementsInMD (
	ZipCode INT Primary Key,
	UploadID VARCHAR,
	Address VARCHAR,
	Enforcement Action and Number VARCHAR,
	Ai Name and ID VARCHAR,
	County VARCHAR,
	Enforcement Action Issued VARCHAR,
	Case Closed VARCHAR,
	Media VARCHAR,
	Program VARCHAR
)

CREATE TABLE MD_data.AverageWage (
	Year INT Primary Key,
	WageOfYear INT,
	DateCreated VARCHAR	
)

CREATE TABLE MD_data.AverageWagePerCounty (
	CountyName VARCHAR Primary Key,
	WageForCounty INT
)

CREATE TABLE MD_data.CountiesInMD (
	CountyName VARCHAR Primary Key,
)


CREATE TABLE MD_data.AirEnforcementsInMD (
	FacilityName VARCHAR Primary Key,
	AchievedDate VARCHAR,
	ActionDescription VARCHAR,
	Address VARCHAR,
	County VARCHAR,
	Documents VARCHAR,
	ZipCode INT
)


