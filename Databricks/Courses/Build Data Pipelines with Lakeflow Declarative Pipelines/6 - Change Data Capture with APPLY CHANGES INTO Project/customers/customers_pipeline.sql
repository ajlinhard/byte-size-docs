-- Databricks notebook source
-- MAGIC %md
-- MAGIC
-- MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
-- MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
-- MAGIC </div>
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC # Customers Pipeline with Change Data Capture

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Run the Pipeline
-- MAGIC To save some time, let's run the entire pipeline for **status**, **orders** and **customers**. While the pipeline is running explore the code cells for the new **customers** flow.
-- MAGIC
-- MAGIC **NOTE:** The **status** and **orders** pipelines are the same as the previous demonstrations.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## A. JSON -> Bronze
-- MAGIC
-- MAGIC  As in the previous notebook, we define a bronze streaming table named **customers_bronze_raw_demo6** using a data source configured with Auto Loader (`FROM STREAM`).
-- MAGIC
-- MAGIC The code below includes:
-- MAGIC
-- MAGIC    - Adds comment for clarity.
-- MAGIC
-- MAGIC    - The table property `pipelines.reset.allowed = false` to prevent deletion of all ingested bronze data if a full refresh is triggered.
-- MAGIC
-- MAGIC    - Creates columns to capture the time of data ingestion and the source file name for each row.

-- COMMAND ----------

CREATE OR REFRESH STREAMING TABLE 1_bronze_db.customers_bronze_raw_demo6
  COMMENT "Raw data from customers CDC feed"
  TBLPROPERTIES (
    "quality" = "bronze",
    "pipelines.reset.allowed" = false     -- prevent full table refreshes on the bronze table
  )
AS 
SELECT 
  *,
  current_timestamp() processing_time,
  _metadata.file_name as source_file
FROM STREAM read_files(
  "${source}/customers", 
  format => "json");

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## B. Data Quality Enforcement
-- MAGIC
-- MAGIC The query below demonstrates:
-- MAGIC
-- MAGIC - The three violation constraint actions: **WARN**, **DROP**, and **FAIL**. Each defines how to handle constraint violations.
-- MAGIC - Applying multiple conditions to a single constraint.
-- MAGIC - Using a built-in SQL function within a constraint.
-- MAGIC
-- MAGIC ### About the data source:
-- MAGIC
-- MAGIC - The data is a CDC feed that contains **`INSERT`**, **`UPDATE`**, and **`DELETE`** operations.  
-- MAGIC - REQUIREMENT: **UPDATE** and **INSERT** operations should contain valid entries for all fields.  
-- MAGIC - REQUIREMENT: **DELETE** operations should contain **`NULL`** values for all fields except the **timestamp**, **customer_id**, and **operation** fields.
-- MAGIC
-- MAGIC **NOTE:** To ensure only valid data reaches our silver table, we’ll write a series of quality enforcement rules that allow expected null values in **DELETE** operations while rejecting bad data elsewhere.
-- MAGIC
-- MAGIC
-- MAGIC ### We'll break down each of these constraints below:
-- MAGIC
-- MAGIC ##### 1. **`valid_id`**
-- MAGIC This constraint will cause our transaction to fail if a record contains a null value in the **`customer_id`** field.
-- MAGIC
-- MAGIC ##### 2. **`valid_operation`**
-- MAGIC This constraint will drop any records that contain a null value in the **`operation`** field.
-- MAGIC
-- MAGIC ##### 3. **`valid_name`**
-- MAGIC This constraint will track any records that contain a null value in the **`name`** field. Because there is no additional instruction for what to do with invalid records, violating rows will be recorded in metrics but not dropped.
-- MAGIC
-- MAGIC ##### 4. **`valid_address`**
-- MAGIC This constraint checks if the **`operation`** field is **`DELETE`**; if not, it checks for null values in any of the 4 fields comprising an address. Because there is no additional instruction for what to do with invalid records, violating rows will be recorded in metrics but not dropped.
-- MAGIC
-- MAGIC ##### 5. **`valid_email`**
-- MAGIC This constraint uses regex pattern matching to check that the value in the **`email`** field is a valid email address. It contains logic to not apply this to records if the **`operation`** field is **`DELETE`** (because these will have a null value for the **`email`** field). Violating records are dropped.
-- MAGIC
-- MAGIC **NOTE:** When a record is going to be dropped, all values except the **customer_id** will be `null`.
-- MAGIC | address                               | city         | customer_id | email                    | name           | operation | state |
-- MAGIC |---------------------------------------|--------------|-------------|--------------------------|----------------|-----------|-------|
-- MAGIC | null                                  | null         | 23617       | null                     | null           | DELETE    | null  |
-- MAGIC

-- COMMAND ----------

CREATE STREAMING TABLE 1_bronze_db.customers_bronze_clean_demo6
  (
    CONSTRAINT valid_id EXPECT (customer_id IS NOT NULL) ON VIOLATION FAIL UPDATE,
    CONSTRAINT valid_operation EXPECT (operation IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_name EXPECT (name IS NOT NULL OR operation = "DELETE"),
    CONSTRAINT valid_address EXPECT (
      (address IS NOT NULL and 
        city IS NOT NULL and 
        state IS NOT NULL and 
        zip_code IS NOT NULL) OR
       operation = "DELETE"),
    CONSTRAINT valid_email EXPECT (
      rlike(email, '^([a-zA-Z0-9_\\-\\.]+)@([a-zA-Z0-9_\\-\\.]+)\\.([a-zA-Z]{2,5})$') OR 
            operation = "DELETE") ON VIOLATION DROP ROW
  )
  COMMENT "Clean raw bronze timestamp column and add data quality constraints"
AS 
SELECT 
  *,
  CAST(from_unixtime(timestamp) AS timestamp) AS timestamp_datetime
FROM STREAM 1_bronze_db.customers_bronze_raw_demo6

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## C. Processing CDC Data with **`APPLY CHANGES INTO`**
-- MAGIC DLT introduces a new syntactic structure for simplifying CDC feed processing.
-- MAGIC
-- MAGIC **`APPLY CHANGES INTO`** has the following guarantees and requirements:
-- MAGIC - Performs incremental/streaming ingestion of CDC data
-- MAGIC - Provides simple syntax to specify one or many fields as the primary key for a table
-- MAGIC - Default assumption is that rows will contain inserts and updates
-- MAGIC - Can optionally apply deletes
-- MAGIC - Automatically orders late-arriving records using user-provided sequencing key (order to process rows)
-- MAGIC - Uses a simple syntax for specifying columns to ignore with the **`EXCEPT`** keyword
-- MAGIC - The default to applying changes is SCD Type 1. We will use SCD Type 2 here.
-- MAGIC
-- MAGIC The code below uses `APPLY CHANGES INTO` to create and update the **2_silver_db.customers_silver_demo6** streaming table using records from the **1_bronze_db.customers_bronze_clean_demo6** streaming table.
-- MAGIC
-- MAGIC [APPLY CHANGES INTO](https://docs.databricks.com/gcp/en/dlt-ref/dlt-sql-ref-apply-changes-into) documentation

-- COMMAND ----------

-- Create the streaming target table if it's not already created
CREATE OR REFRESH STREAMING TABLE 2_silver_db.customers_silver_demo6
  COMMENT 'SCD Type 2 Historical Customer Data';


-- Apply CDC changes from the cleaned bronze stream to the silver table using SCD Type 2
APPLY CHANGES INTO 2_silver_db.customers_silver_demo6   -- Target table to update
  FROM STREAM 1_bronze_db.customers_bronze_clean_demo6  -- Source records to determine updates, deletes and inserts
  KEYS (customer_id)                              -- Primary key for identifying records
  APPLY AS DELETE WHEN operation = "DELETE"       -- Handle deletes from source to the target
  SEQUENCE BY timestamp_datetime                  -- Defines order of operations for applying changes
  COLUMNS * EXCEPT (timestamp, _rescued_data, operation)     -- Select columns and exclude metadata fields
  STORED AS SCD TYPE 2;                           -- Use Slowly Changing Dimension Type 2 to keep historical data

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## D. Querying Tables with Applied Changes
-- MAGIC
-- MAGIC The `APPLY CHANGES INTO` statement defaults to a Type 1 SCD table, where each key has a single current record and updates overwrite existing data. In this case, we're using Type 2 SCD to preserve historical changes.
-- MAGIC
-- MAGIC
-- MAGIC #### Important
-- MAGIC Although **customers_silver_demo6** is defined as a streaming table, applying updates and deletes makes it unsuitable as a streaming source for downstream operations due to the violation of append-only constraints.
-- MAGIC
-- MAGIC This approach ensures that out-of-order updates can be properly reconciled and that deleted records are excluded from downstream results.
-- MAGIC
-- MAGIC The cell below defines a materialized view from the **customers_silver_demo6** table to store only the **current customer data** for use in downstream analysis, joins or other processing by querying for all `null` values in the **__END_AT** column.

-- COMMAND ----------

CREATE OR REFRESH MATERIALIZED VIEW 3_gold_db.current_customers_gold_demo6
COMMENT "Current updated list of active customers"
AS 
SELECT 
  * EXCEPT (processing_time),
  current_timestamp() updated_at
FROM 2_silver_db.customers_silver_demo6
WHERE `__END_AT` IS NULL;      -- Filter for only rows that contain a null value for __END_AT, which indicates the current version of the record

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## E. Explore the Pipeline Results
-- MAGIC
-- MAGIC After running the pipeline and reviewing the code cells, take time to explore the pipeline results for the **customers** flow following the steps below.
-- MAGIC
-- MAGIC **Run with 1 JSON File**
-- MAGIC
-- MAGIC ![demo6_cdc_run01.png](../../Includes/images/demo6_cdc_run01.png)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. In the **customers** flow in the pipeline graph, notice that **939** rows were streamed into the three streaming tables and the materialized view. This is because all records are new and valid entries, they were ingested throughout the flow.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. In the table below, find the **customers_silver_demo6** table and note the following:
-- MAGIC
-- MAGIC   - The **Upserted** column indicates that all **939** rows were upserted into the table, as all rows are new.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. Leave this pipeline open and navigate back to the **6 - Change Data Capture with APPLY INTO** notebook and follow the steps in **D. Land New Data to Your Data Source Volume** and then run the pipeline.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 4. After you have explored and landed  1 new JSON file to each of your data sources, complete the following to explore the **customers** flow in the **Pipeline graph**:
-- MAGIC
-- MAGIC    a. 23 rows were read into the **customers_bronze_raw_demo6** and **customers_bronze_clean_demo6** streaming tables (from the new **01.json** file) since all data quality checks passed.
-- MAGIC
-- MAGIC    b. In the **customers_silver_demo6** streaming table (CDC SCD Type 2), 35 rows were processed and **upserted** into the table:
-- MAGIC    
-- MAGIC       - **12 updates** (each consisting of updating the original row to inactive, and adding a new row, for a total of **24** upserts)  
-- MAGIC       - **1** row was marked as deleted (value added for the **__END_AT** column)  
-- MAGIC       - **10** new customers were added  
-- MAGIC       - Total changes: 24 + 1 + 10 = **35**

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. Navigate back to the **6 - Change Data Capture with APPLY INTO** notebook and follow the steps in **E. View the CDC SCD Type 2 on the Customers Table**.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC
-- MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
-- MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
-- MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
-- MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>