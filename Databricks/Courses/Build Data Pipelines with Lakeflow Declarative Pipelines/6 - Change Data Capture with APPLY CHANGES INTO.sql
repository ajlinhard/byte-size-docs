-- Databricks notebook source
-- MAGIC %md
-- MAGIC
-- MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
-- MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
-- MAGIC </div>
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC # 6 - Change Data Capture with APPLY CHANGES INTO
-- MAGIC
-- MAGIC In this demonstration, we will continue to build our pipeline by ingesting **customer** data into our pipeline. The customer data includes new customers, customers who have deleted their accounts, and customers who have updated their information (such as address, email, etc.). We will need to build our customer pipeline by implementing change data capture (CDC) for customer data.
-- MAGIC
-- MAGIC The customer pipeline flow will:
-- MAGIC
-- MAGIC - The bronze table uses **Auto Loader** to ingest JSON data from cloud object storage with SQL (`FROM STREAM`).
-- MAGIC - A table is defined to enforce constraints before passing records to the silver layer.
-- MAGIC - `APPLY CHANGES INTO` is used to automatically process CDC data into the silver layer as a Type 2 [slowly changing dimension (SCD) table](https://en.wikipedia.org/wiki/Slowly_changing_dimension).
-- MAGIC - A gold table is defined to create a materialized view of the current customers with updated information (dropped customers, new customers and updated information).
-- MAGIC
-- MAGIC
-- MAGIC
-- MAGIC ### Learning Objectives
-- MAGIC
-- MAGIC By the end of this lesson, students should feel comfortable:
-- MAGIC - Apply the `APPLY CHANGES INTO` operation in Lakeflow Declarative Pipelines to process change data capture (CDC) by integrating and updating incoming data from a source stream into an existing Delta table, ensuring data accuracy and consistency.
-- MAGIC - Analyze Slowly Changing Dimensions (SCD Type 2) tables within Lakeflow Declarative Pipelines to effectively track historical changes in dimensional data, managing the state of records over time using appropriate keys, versioning, and timestamps.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## REQUIRED - SELECT CLASSIC COMPUTE
-- MAGIC
-- MAGIC Before executing cells in this notebook, please select your classic compute cluster in the lab. Be aware that **Serverless** is enabled by default.
-- MAGIC
-- MAGIC Follow these steps to select the classic compute cluster:
-- MAGIC
-- MAGIC 1. Navigate to the top-right of this notebook and click the drop-down menu to select your cluster. By default, the notebook will use **Serverless**.
-- MAGIC
-- MAGIC 1. If your cluster is available, select it and continue to the next cell. If the cluster is not shown:
-- MAGIC
-- MAGIC     - In the drop-down, select **More**.
-- MAGIC
-- MAGIC     - In the **Attach to an existing compute resource** pop-up, select the first drop-down. You will see a unique cluster name in that drop-down. Please select that cluster.
-- MAGIC
-- MAGIC **NOTE:** If your cluster has terminated, you might need to restart it in order to select it. To do this:
-- MAGIC
-- MAGIC 1. Right-click on **Compute** in the left navigation pane and select *Open in new tab*.
-- MAGIC
-- MAGIC 1. Find the triangle icon to the right of your compute cluster name and click it.
-- MAGIC
-- MAGIC 1. Wait a few minutes for the cluster to start.
-- MAGIC
-- MAGIC 1. Once the cluster is running, complete the steps above to select your cluster.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## A. Classroom Setup
-- MAGIC
-- MAGIC Run the following cell to configure your working environment for this course. This setup will reset your volume to one JSON file in each directory.
-- MAGIC
-- MAGIC **NOTE:** The `DA` object is only used in Databricks Academy courses and is not available outside of these courses. It will dynamically create and reference the information needed to run the course.

-- COMMAND ----------

-- MAGIC %run ./Includes/Classroom-Setup-6

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## B. Explore the Customer Data Source Files

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Run the cell below to programmatically view the files in your `/Volumes/dbacademy/ops/lab-user-name/customers` volume. Confirm you only see one **00.json** file for customers.

-- COMMAND ----------

-- DBTITLE 1,View files in the customers volume
-- MAGIC %python
-- MAGIC spark.sql(f'LIST "{DA.paths.working_dir}/customers"').display()

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Run the query below to explore the customers **00.json** file located at `/Volumes/dbacademy/ops/lab-user-name/customers`. Note the following:
-- MAGIC
-- MAGIC    a. The file contains **939 customers** (remember this number).
-- MAGIC
-- MAGIC    b. It includes general customer information such as **email**, **name**, and **address**.
-- MAGIC
-- MAGIC    c. The **timestamp** column specifies the logical order of customer events in the source data.
-- MAGIC
-- MAGIC    d. The **operation** column indicates whether the entry is for a new customer, a deletion, or an update.
-- MAGIC       - **NOTE:** Since this is the first JSON file, all rows will be considered new customers.
-- MAGIC

-- COMMAND ----------

-- DBTITLE 1,Explore the customers raw JSON data
SELECT *
FROM read_files(
  DA.paths_working_dir || '/customers/00.json',
  format => "JSON"
)
ORDER BY operation;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Question: 
-- MAGIC How can we ingest new raw data source files (JSON) with customer updates into our pipeline to update the **customers_silver** table when inserts, updates, or deletes occur, while also maintaining historical records?

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## C. Change Data Capture with APPLY CHANGES INTO in Lakeflow Declarative Pipelines for SCD Type 2
-- MAGIC **SCD - Slowly Changing Dimensions**

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Run the cell below to create your starter Lakeflow Declarative Pipeline for this demonstration. The pipeline will set the following for you:
-- MAGIC     - Your default catalog: `labuser`
-- MAGIC     - Your configuration parameter: `source` = `/Volumes/dbacademy/ops/your-labuser-name`
-- MAGIC
-- MAGIC     **NOTE:** If the pipeline already exists, an error will be returned. In that case, you'll need to delete the existing pipeline and rerun this cell.
-- MAGIC
-- MAGIC     To delete the pipeline:
-- MAGIC
-- MAGIC     a. Select **Pipelines** from the far-left navigation bar.  
-- MAGIC
-- MAGIC     b. Find the pipeline you want to delete.  
-- MAGIC
-- MAGIC     c. Click the three-dot menu ![ellipsis icon](./Includes/images/ellipsis_icon.png).  
-- MAGIC
-- MAGIC     d. Select **Delete**.
-- MAGIC
-- MAGIC **NOTE:**  The `create_declarative_pipeline` function is a custom function built for this course to create the sample pipeline using the Databricks REST API. This avoids manually creating the pipeline and referencing the pipeline assets.

-- COMMAND ----------

-- DBTITLE 1,Create pipeline 6
-- MAGIC %python
-- MAGIC create_declarative_pipeline(pipeline_name=f'6 - Change Data Capture with APPLY CHANGES INTO - {DA.catalog_name}', 
-- MAGIC                             root_path_folder_name='6 - Change Data Capture with APPLY CHANGES INTO Project',
-- MAGIC                             catalog_name = DA.catalog_name,
-- MAGIC                             schema_name = 'default',
-- MAGIC                             source_folder_names=['orders', 'status', 'customers'],
-- MAGIC                             configuration = {'source':DA.paths.working_dir})

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Complete the following steps to open the starter Lakeflow Declarative Pipeline project for this demonstration:
-- MAGIC
-- MAGIC    a. Click the folder icon ![Folder](./Includes/images/folder_icon.png) in the left navigation panel.
-- MAGIC
-- MAGIC    b. In the **Build Data Pipelines with Lakeflow Declarative Pipelines** folder, find the **6 - Change Data Capture with APPLY CHANGES INTO Project** folder. 
-- MAGIC    
-- MAGIC    c. Right-click and select **Open in a new tab**.
-- MAGIC
-- MAGIC    d. In the new tab you should see three folders: **explorations**, **orders**, **status** and **customers**. 
-- MAGIC
-- MAGIC       - **NOTE:** The **status** and **orders** pipelines are the same as we saw in the previous demo.
-- MAGIC
-- MAGIC    e. Open the **customers** folder and select the **customers_pipeline** notebook.
-- MAGIC
-- MAGIC #### IMPORTANT
-- MAGIC    **NOTE:** If you open the **customers_pipeline** file and it does not open up the pipeline editor, that is because that folder is not associated with a pipeline. Please make sure to run the previous cell to associate the folder with the pipeline and try again.
-- MAGIC
-- MAGIC    **WARNING:** If you get the following warning when opening the **orders_pipeline.sql** file: 
-- MAGIC
-- MAGIC    ```pipeline you are trying to access does not exist or is inaccessible. Please verify the pipeline ID, request access or detach this file from the pipeline.``` 
-- MAGIC
-- MAGIC    Simply refresh the page and/or reselect the notebook.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. Explore the **customers_pipeline** notebook code cells step by step and then follow the instructions.
-- MAGIC
-- MAGIC     **NOTE:** The **status** and **orders** code is the same as the previous demonstration, you do not need to review those.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## D. Land New Data to Your Data Source Volume

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Before landing more data into your cloud storage location, run the query below to view the **customers_silver_demo6** streaming table (the table with SCD Type 2). Notice the following:
-- MAGIC
-- MAGIC    - The streaming table contains all **939 rows** from the **00.json** file, since they are all new customers being added to the table.
-- MAGIC
-- MAGIC    - Scroll to the right of the table and note that `APPLY CHANGES INTO` added the following columns:
-- MAGIC
-- MAGIC      - **__START_AT**:  
-- MAGIC        - A timestamp representing when the current version of a record became active.  
-- MAGIC
-- MAGIC      - **__END_AT**:  
-- MAGIC        - A timestamp representing when the current version of a record became inactive (either a **DELETE** or **UPDATE**).
-- MAGIC        - This means if you filter on **__END_AT** for `null` you retrieve all active customers. In the first run all customer rows are active.
-- MAGIC
-- MAGIC      - **NOTE:** These columns support Slowly Changing Dimension (SCD) Type 2. The special fields **__START_AT** and **__END_AT** are automatically managed by the `APPLY CHANGES` statement in Databricks to track the validity period of each version of a record.
-- MAGIC
-- MAGIC In this initial ingestion of the **00.json** file, all records are active, so the **__END_AT** column contains only `null` values.

-- COMMAND ----------

-- DBTITLE 1,Explore the CDC SCD2 Streaming Table
SELECT *
FROM 2_silver_db.customers_silver_demo6;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Query the **customers_silver_demo6** streaming table for the customer with **customer_id** *23225*. Notice that this customer has:
-- MAGIC
-- MAGIC    - **Address**: `76814 Jacqueline Mountains Suite 815`  
-- MAGIC
-- MAGIC    - **State**: `TX`  
-- MAGIC
-- MAGIC    - **__END_AT**: Contains a `null` value, indicating this is the current information for that customer.

-- COMMAND ----------

-- DBTITLE 1,View a customer in the CDC ST
SELECT *
FROM 2_silver_db.customers_silver_demo6
WHERE customer_id = 23225;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. Run the cell below to land a new JSON file to each volume (**customers**, **status** and **orders**) to simulate new files being added to your cloud storage locations.

-- COMMAND ----------

-- DBTITLE 1,Land new files in your volumes
-- MAGIC %python
-- MAGIC copy_file_for_multiple_sources(copy_n_files = 2, 
-- MAGIC                                sleep_set = 1,
-- MAGIC                                copy_from_source='/Volumes/dbacademy_retail/v01/retail-pipeline',
-- MAGIC                                copy_to_target = DA.paths.working_dir)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 4. Run the cell below to programmatically view the files in your `/Volumes/dbacademy/ops/labuser-name/customers` volume. Confirm your volume now contains **00.json** and **01.json** file.

-- COMMAND ----------

-- DBTITLE 1,View files in your customers volume
-- MAGIC %python
-- MAGIC spark.sql(f'LIST "{DA.paths.working_dir}/customers"').display()

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 5. Run the cell to explore the raw data in the **01.json** file prior to ingesting it in your pipeline. Notice the following:
-- MAGIC
-- MAGIC    - This file contains **23** rows.
-- MAGIC
-- MAGIC    - The **operation** column specifies **UPDATE**, **DELETE**, and **NEW** operations for customers.
-- MAGIC       - **NOTE:** There are:
-- MAGIC          - 12 customers with **UPDATE** values
-- MAGIC          - 1 customer with a **DELETE** value
-- MAGIC          - 10 new customers with a **NEW** value
-- MAGIC
-- MAGIC    - In the results below, find the row with **customer_id** *23225* and note the following:
-- MAGIC
-- MAGIC       - The original address for **Sandy Adams** (from the streaming table, file **00.json**) was: `76814 Jacqueline Mountains Suite 815`, `TX`
-- MAGIC
-- MAGIC       - The updated address for **Sandy Adams** (from the file below) is: `512 John Stravenue Suite 239`, `TN`
-- MAGIC
-- MAGIC    - In the results below, find the row with **customer_id** *23617* and note the following:
-- MAGIC       - The **operation** for this customer is **DELETE**.
-- MAGIC       - When the **operation** column is delete, all other column values are `null`.

-- COMMAND ----------

-- DBTITLE 1,Explore the new 01.json file
SELECT *
FROM read_files(
  DA.paths_working_dir || '/customers/01.json',
  format => "JSON"
)
ORDER BY customer_id;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 6. Go back to your pipeline and run the pipeline to process a new JSON file for each data source.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## E. View the CDC SCD Type 2 on the Customers Table

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. View the data in the **customers_silver_demo6** streaming table with SCD Type 2 and observe the following:
-- MAGIC
-- MAGIC    a. The table contains **961 rows** (**initial 939 customers** + **12 updates** to existing customers + **10 new customers**).
-- MAGIC
-- MAGIC    b. Scroll to the right and locate the **__END_AT** column. Then scroll down to rows **82** and **83**. Notice there are two rows for customer **22668**, the original record and the updated record.
-- MAGIC
-- MAGIC **NOTE:** For demonstration purposes, many of the metadata columns were retained in the silver streaming table.

-- COMMAND ----------

-- DBTITLE 1,View the updated CDC ST
SELECT customer_id, address, name, __START_AT, __END_AT
FROM 2_silver_db.customers_silver_demo6
ORDER BY customer_id, __END_AT;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Run the query on the **2_silver_db.customers_silver_demo6** streaming table for all rows where **__END_AT** `IS NOT NULL` to view all rows where those customers rows are now inactive.
-- MAGIC
-- MAGIC Notice the following:
-- MAGIC   - **13 rows** are returned (**12 UPDATES** + **1 DELETE**)
-- MAGIC   - The **__END_AT** column indicates the date and time that the row was either updated or deleted.

-- COMMAND ----------

-- DBTITLE 1,View inactive/historical rows
SELECT customer_id, address, name, __START_AT, __END_AT
FROM 2_silver_db.customers_silver_demo6
WHERE __END_AT IS NOT NULL;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. Query the **2_silver_db.customers_silver** table for the **customer_id** *23225*. Notice the following:
-- MAGIC
-- MAGIC
-- MAGIC     - There are **two records** for that customer in the table.
-- MAGIC     - The original record from the **00.json** file now has a value in the **__END_AT** column, indicating that it is now inactive.
-- MAGIC     - The new record from the **01.json** file is now the active row and contains a `null` value in the **__END_AT** column.

-- COMMAND ----------

-- DBTITLE 1,View the updated customer 23225
SELECT customer_id, address, name, state, source_file, __START_AT, __END_AT
FROM 2_silver_db.customers_silver_demo6
WHERE customer_id = 23225;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 4. In the **01.json** file, **customer_id** *23617* was marked as deleted. Let's query the **customers_silver_demo6** table for that customer and view the results. Notice that when a customer is marked as deleted, the **__END_AT** column contains the value of when that customer was deleted and became inactive.
-- MAGIC

-- COMMAND ----------

-- DBTITLE 1,View the 'inactive/deleted' row
SELECT customer_id, address, name, __START_AT, __END_AT
FROM 2_silver_db.customers_silver_demo6
WHERE customer_id = 23617

-- COMMAND ----------

-- MAGIC %md
-- MAGIC **BONUS:** The query below is a dynamic query to find **ALL** deleted records from the silver table (in run 2 that is one customer, the customer above) using a window function. The query:
-- MAGIC   - Finds the latest record of each customer.
-- MAGIC   - If the latest record of each customer has a date value in the **__END_AT** column it means that the customer has requested to be deleted.

-- COMMAND ----------

-- Create a temporary view of the latest customer records for each customer
CREATE OR REPLACE TEMPORARY VIEW latest_customer_records AS
SELECT
  customer_id, 
  address, 
  name, 
  __START_AT, 
  __END_AT,
  ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY __START_AT DESC) AS latest_record -- Get the latest record of each customer
FROM 2_silver_db.customers_silver_demo6
QUALIFY latest_record = 1;


-- Show all customers who were deleted (only 1 customer)
SELECT
  customer_id, 
  address, 
  name, 
  __START_AT, 
  __END_AT
FROM latest_customer_records
WHERE __END_AT IS NOT NULL;   -- Query for the latest value of each customer where it is not null. It will display all 'deleted' customers.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 5. To view your organization's most up-to-date customer data, you can query the materialized view **3_gold_db.current_customers_gold_demo6**. Remember, the query to create the materialized view filters for all **__END_AT** values that are `null` (active rows).
-- MAGIC
-- MAGIC     Run the cell and view the results. Notice the following:
-- MAGIC    - The current updated list of customers contains **948 rows**:
-- MAGIC      - **939** from the initial file (**00.json**)
-- MAGIC      - **+10** new customers from the update file (**01.json**)
-- MAGIC      - **-1** deleted customer from the update file (**01.json**)
-- MAGIC      - The table also contains the updated records from the **01.json** file.
-- MAGIC
-- MAGIC **Gold Customers Materialized View**
-- MAGIC ```
-- MAGIC CREATE MATERIALIZED VIEW 3_gold_db.current_customers_gold_demo6
-- MAGIC COMMENT "Current updated list of active customers"
-- MAGIC AS 
-- MAGIC SELECT 
-- MAGIC   * EXCEPT (processing_time),
-- MAGIC   current_timestamp() updated_at
-- MAGIC FROM 2_silver_db.customers_silver
-- MAGIC WHERE `__END_AT` IS NULL;  
-- MAGIC ```
-- MAGIC
-- MAGIC **NOTE:** For demonstration purposes, many of the metadata columns were kept in the materialized view.

-- COMMAND ----------

SELECT customer_id, address, name, __START_AT, __END_AT
FROM 3_gold_db.current_customers_gold_demo6;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Additional Resources
-- MAGIC
-- MAGIC - [What is change data capture (CDC)?](https://docs.databricks.com/aws/en/dlt/what-is-change-data-capture)
-- MAGIC
-- MAGIC - [APPLY CHANGES INTO](https://docs.databricks.com/gcp/en/dlt-ref/dlt-sql-ref-apply-changes-into) documentation
-- MAGIC
-- MAGIC - [The AUTO CDC APIs: Simplify change data capture with Lakeflow Declarative Pipelines](https://docs.databricks.com/aws/en/dlt/cdc) documentation
-- MAGIC
-- MAGIC - [How to implement Slowly Changing Dimensions when you have duplicates - Part 1: What to look out for?](https://community.databricks.com/t5/technical-blog/how-to-implement-slowly-changing-dimensions-when-you-have/ba-p/40568)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC
-- MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
-- MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
-- MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
-- MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>