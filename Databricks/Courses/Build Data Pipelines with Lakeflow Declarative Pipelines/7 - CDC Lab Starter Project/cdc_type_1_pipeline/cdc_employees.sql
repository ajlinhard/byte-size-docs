------------------------------------------------------
-- CHANGE DATA CAPTURE WITH SCD TYPE 1 LAB
------------------------------------------------------
-- TO DO: Explore the code and complete the APPLY CHANGES INTO STATEMENT
------------------------------------------------------


------------------------------------------------
-- A. CSV -> BRONZE STREAMING TABLE
------------------------------------------------
-- Adds the "pipelines.reset.allowed" = false property to prevent full refreshes on the initial ingestion layer
------------------------------------------------
-- REQUIREMENTS:
  -- Simply review the completed code below
------------------------------------------------
CREATE OR REFRESH STREAMING TABLE lab_1_bronze_db.employees_raw_bronze_demo7
  COMMENT "Raw ingestion from CSV files"
  TBLPROPERTIES (
      "quality" = "bronze", 
      "pipelines.reset.allowed" = false    -- prevent full table refreshes on the bronze table
  )             
AS 
SELECT
  *,
  current_timestamp() AS ingestion_time,
  _metadata.file_name AS source_file
FROM STREAM read_files(
  '${source}',
  format => 'CSV'
);


--------------------------------------------------------------
-- B. BRONZE STREAMING TABLE -> BRONZE CLEAN STREAMING TABLE
--------------------------------------------------------------
-- Add data quality constraints
-- Select the necessary columns and perform minor transformations
--------------------------------------------------------------
-- REQUIREMENTS:
  -- Simply review the completed code below.
--------------------------------------------------------------
CREATE OR REFRESH STREAMING TABLE lab_1_bronze_db.employees_bronze_clean_demo7
  (
    CONSTRAINT valid_emp_id EXPECT (EmployeeID IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_country EXPECT (Country IN ('US','GR'))
  )
  COMMENT "Clean the raw bronze table and prepare for CDC SCD Type 1"
  TBLPROPERTIES (
      "quality" = "bronze_cleaned_for_cdc" 
  )   
AS 
SELECT
  EmployeeID,
  FirstName,
  upper(Country) AS Country,
  Department,
  Salary,
  HireDate,
  Operation,
  ProcessDate
FROM STREAM lab_1_bronze_db.employees_raw_bronze_demo7;


--------------------------------------------------------------
-- C. BRONZE CLEAN STREAMING TABLE -> SILVER CDC STREAMING TABLE (SCD TYPE 1)
--------------------------------------------------------------
-- REQUIREMENTS:
  -- Complete the `APPLY CHANGES INTO` statement
  -- Use the `lab_2_silver_db.current_employees_silver_demo7` as the target
  -- Use the `lab_1_bronze_db.employees_bronze_clean_demo7` as the source
  -- Perform SCD Type 1 (the default)
  -- Delete all rows marked as 'delete'
  -- Select all columns except `operation`
--------------------------------------------------------------
-- TO DO: Complete the APPLY CHANGES INTO STATEMENT
--------------------------------------------------------------

-- Create the empty streaming table
CREATE OR REFRESH STREAMING TABLE lab_2_silver_db.current_employees_silver_demo7;

-- Perform CDC SCD Type 1
APPLY CHANGES INTO lab_2_silver_db.current_employees_silver_demo7
FROM STREAM <FILL-IN>
KEYS (<FILL-IN>)
APPLY AS DELETE WHEN <FILL-IN>
SEQUENCE BY <FILL-IN>
COLUMNS * EXCEPT (<FILL-IN>)  -- Select all columns except the operation column
STORED AS <FILL-IN>;