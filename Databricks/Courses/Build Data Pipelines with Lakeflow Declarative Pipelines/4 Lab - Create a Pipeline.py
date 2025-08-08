# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # 4 Lab - Create a Pipeline  
# MAGIC ### Estimated Duration: ~15-20 minutes
# MAGIC
# MAGIC In this lab, you'll migrate a traditional ETL workflow to a pipeline for incremental data processing. You'll practice building streaming tables and materialized views using Lakeflow Declarative Pipelines syntax.
# MAGIC
# MAGIC #### Your Tasks:
# MAGIC - Create a new Pipeline  
# MAGIC - Convert traditional SQL ETL to declarative syntax for incremental processing 
# MAGIC - Configure pipeline settings  
# MAGIC - Define data quality expectations  
# MAGIC - Validate and run the pipeline
# MAGIC
# MAGIC ### Learning Objectives
# MAGIC
# MAGIC By the end of this lesson, you will be able to:
# MAGIC - Create a pipeline and execute it successfully using the new multi file editor.
# MAGIC - Modify and configure pipeline settings to align with specific data processing requirements.
# MAGIC - Integrate data quality expectations into a pipeline and evaluate their effectiveness.

# COMMAND ----------

# MAGIC %md
# MAGIC ## REQUIRED - SELECT CLASSIC COMPUTE
# MAGIC
# MAGIC Before executing cells in this notebook, please select your classic compute cluster in the lab. Be aware that **Serverless** is enabled by default.
# MAGIC
# MAGIC Follow these steps to select the classic compute cluster:
# MAGIC
# MAGIC 1. Navigate to the top-right of this notebook and click the drop-down menu to select your cluster. By default, the notebook will use **Serverless**.
# MAGIC
# MAGIC 1. If your cluster is available, select it and continue to the next cell. If the cluster is not shown:
# MAGIC
# MAGIC     - In the drop-down, select **More**.
# MAGIC
# MAGIC     - In the **Attach to an existing compute resource** pop-up, select the first drop-down. You will see a unique cluster name in that drop-down. Please select that cluster.
# MAGIC
# MAGIC **NOTE:** If your cluster has terminated, you might need to restart it in order to select it. To do this:
# MAGIC
# MAGIC 1. Right-click on **Compute** in the left navigation pane and select *Open in new tab*.
# MAGIC
# MAGIC 1. Find the triangle icon to the right of your compute cluster name and click it.
# MAGIC
# MAGIC 1. Wait a few minutes for the cluster to start.
# MAGIC
# MAGIC 1. Once the cluster is running, complete the steps above to select your cluster.

# COMMAND ----------

# MAGIC %md
# MAGIC ## A. Classroom Setup
# MAGIC
# MAGIC Run the following cell to configure your working environment for this course.
# MAGIC
# MAGIC **NOTE:** The `DA` object is only used in Databricks Academy courses and is not available outside of these courses. It will dynamically create and reference the information needed to run the course.

# COMMAND ----------

# MAGIC %run ./Includes/Classroom-Setup-4

# COMMAND ----------

# MAGIC %md
# MAGIC ## B. SCENARIO
# MAGIC
# MAGIC Your data engineering team has identified an opportunity to modernize an existing ETL pipeline that was originally developed in a Databricks notebook. While the current pipeline gets the job done, it lacks the scalability, observability, efficiency and automated data quality features required as your data volume and complexity grow.
# MAGIC
# MAGIC To address this, you've been asked to migrate the existing pipeline to a Lakeflow Declarative Pipeline. Lakeflow Declarative Pipelines will enable your team to define data transformations more declaratively, apply data quality rules, and benefit from built-in optimization, lineage tracking and monitoring.
# MAGIC
# MAGIC Your goal is to refactor the original notebook based logic (shown in the cells below) into a Lakeflow Declarative Pipeline.
# MAGIC
# MAGIC ### REQUIREMENTS:
# MAGIC   - Migrate the ETL code below to a Lakeflow Declarative Pipeline.
# MAGIC   - Add the required data quality expectations to the bronze table and silver table:
# MAGIC   - Create materialized views for the most up to date aggregated information.
# MAGIC
# MAGIC Follow the steps below to complete your task.

# COMMAND ----------

# MAGIC %md
# MAGIC ### B1. Explore the Raw Data
# MAGIC
# MAGIC 1. Complete the following steps to view where our lab's streaming raw source files are coming from:
# MAGIC
# MAGIC    a. Select the **Catalog** icon ![Catalog Icon](./Includes/images/catalog_icon.png) in the left navigation bar.  
# MAGIC    
# MAGIC    b. Expand your **labuser** catalog.  
# MAGIC    
# MAGIC    c. Expand the **default** schema.  
# MAGIC    
# MAGIC    d. Expand **Volumes**.  
# MAGIC    
# MAGIC    e. Expand the **lab_files** volume.  
# MAGIC    
# MAGIC    f. You should see a single CSV file named **employees_1.csv**. If not, refresh the catalogs.  
# MAGIC    
# MAGIC    g. The files in the **lab_files** volume will be the data source files you will be ingesting.

# COMMAND ----------

# MAGIC %md
# MAGIC 2. Run the cell below to view the raw CSV file in your **lab_files** volume. Notice the following:
# MAGIC
# MAGIC    - It’s a simple CSV file separated by commas.  
# MAGIC    - It contains headers.  
# MAGIC    - It has 7 rows in total (6 data records and 1 header row).  
# MAGIC    - The first record (row 2) is a test record and should not be included in the pipeline and will be dropped by a data quality expectation.

# COMMAND ----------

spark.sql(f'''
        SELECT *
        FROM csv.`/Volumes/{DA.catalog_name}/default/lab_files/`
        ''').display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### B2. Current ETL Code
# MAGIC
# MAGIC Run each cell below to view the results of the current ETL pipeline. This will give you an idea of the expected output. Don’t worry too much about the data transformations within the SQL queries.
# MAGIC
# MAGIC The focus of this lab is on using **declarative SQL** and creating a **Lakeflow Declarative Pipeline**. You will not need to modify the transformation logic, only the `CREATE` statements and `FROM` clauses to ensure data is read and processed incrementally in your pipeline.

# COMMAND ----------

# MAGIC %md
# MAGIC #### B2.1 - CSV to Bronze
# MAGIC
# MAGIC Explore the code and run the cell. Observe the results. Notice that:
# MAGIC
# MAGIC - The CSV file in the volume is read in as a table named **employees_bronze_lab4** in the **labuser.lab_1_bronze_db** schema.  
# MAGIC - The table contains 6 rows with the correct column names.
# MAGIC
# MAGIC Think about what you will need to change when migrating this to a Lakeflow Declarative Pipeline. Hints are added as comments in the code below.
# MAGIC
# MAGIC **NOTE:** In your Lakeflow Declarative Pipeline we will want to add data quality expectations to document any bad data coming into the pipeline.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Specify to use your labuser catalog from the course DA object
# MAGIC USE CATALOG IDENTIFIER(DA.catalog_name);
# MAGIC
# MAGIC
# MAGIC CREATE OR REPLACE TABLE lab_1_bronze_db.employees_bronze_lab4  -- You will have to modify this to create a streaming table in the pipeline
# MAGIC AS
# MAGIC SELECT 
# MAGIC   *,
# MAGIC   current_timestamp() AS ingestion_time,
# MAGIC   _metadata.file_name as raw_file_name
# MAGIC FROM read_files(                                           -- You will have to modify FROM clause to incrementally read in data
# MAGIC   '/Volumes/' || DA.catalog_name || '/default/lab_files',  -- You will have to modify this path in the pipeline to your specific raw data source
# MAGIC   format => 'CSV',
# MAGIC   header => 'true'
# MAGIC );
# MAGIC
# MAGIC
# MAGIC -- Display table
# MAGIC SELECT *
# MAGIC FROM lab_1_bronze_db.employees_bronze_lab4;

# COMMAND ----------

# MAGIC %md
# MAGIC #### B2.2 - Bronze to Silver
# MAGIC
# MAGIC Run the cell below to create the table **labuser.lab_2_silver_db.employees_silver_lab4** and explore the results. Notice that a few simple data transformations were applied to the bronze table, and metadata columns were removed.
# MAGIC
# MAGIC Think about what you will need to change when migrating this to a Lakeflow Declarative Pipeline. Hints are added as comments in the code below.
# MAGIC
# MAGIC **NOTE:** For simplicity, we are leaving the **test** row in place, and you will remove it using data quality expectations. Typically, we could have just filtered out the null value(s).

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE lab_2_silver_db.employees_silver_lab4 -- You will have to modify this to create a streaming table in the pipeline
# MAGIC AS
# MAGIC SELECT
# MAGIC   EmployeeID,
# MAGIC   FirstName,
# MAGIC   upper(Country) AS Country,
# MAGIC   Department,
# MAGIC   Salary,
# MAGIC   HireDate,
# MAGIC   date_format(HireDate, 'MMMM') AS HireMonthName,
# MAGIC   year(HireDate) AS HireYear, 
# MAGIC   Operation
# MAGIC FROM lab_1_bronze_db.employees_bronze_lab4;                    -- You will have to modify FROM clause to incrementally read in data
# MAGIC
# MAGIC
# MAGIC -- Display table
# MAGIC SELECT *
# MAGIC FROM lab_2_silver_db.employees_silver_lab4;

# COMMAND ----------

# MAGIC %md
# MAGIC #### B2.3 - Silver to Gold
# MAGIC The code below creates two traditional views to aggregate the silver tables.

# COMMAND ----------

# MAGIC %md
# MAGIC 1. Run the cell to create a view that calculates the total number of employees and total salary by country.
# MAGIC
# MAGIC     Think about what you will need to change when migrating this to a Lakeflow Declarative Pipeline. A hint is added as a comment in the code below.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW lab_3_gold_db.employees_by_country_gold_lab4 -- You will have to modify this to create a materialized view in the pipeline
# MAGIC AS
# MAGIC SELECT 
# MAGIC   Country,
# MAGIC   count(*) AS TotalEmployees,
# MAGIC   sum(Salary) AS TotalSalary
# MAGIC FROM lab_2_silver_db.employees_silver_lab4
# MAGIC GROUP BY Country;
# MAGIC
# MAGIC
# MAGIC -- Display view
# MAGIC SELECT *
# MAGIC FROM lab_3_gold_db.employees_by_country_gold_lab4;

# COMMAND ----------

# MAGIC %md
# MAGIC 2. Run the cell to create a view that calculates the salary by department.
# MAGIC
# MAGIC     Think about what you will need to change when migrating this to a Lakeflow Declarative Pipeline. A hint is added as a comment in the code below.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW lab_3_gold_db.salary_by_department_gold_lab4  -- You will have to modify this to create a materialized view in the pipeline
# MAGIC AS
# MAGIC SELECT
# MAGIC   Department,
# MAGIC   sum(Salary) AS TotalSalary
# MAGIC FROM lab_2_silver_db.employees_silver_lab4
# MAGIC GROUP BY Department;
# MAGIC
# MAGIC
# MAGIC -- Display view
# MAGIC SELECT *
# MAGIC FROM lab_3_gold_db.salary_by_department_gold_lab4;

# COMMAND ----------

# MAGIC %md
# MAGIC #### B2.4 - Delete the Tables
# MAGIC
# MAGIC Run the cell below to delete all the tables you created above. You will recreate them as streaming tables and materialized views in the Lakeflow Declarative Pipeline.
# MAGIC
# MAGIC **NOTE:** If you have created the streaming tables and materialized views with Lakeflow Declarative Pipelines and want to drop them to redo this lab, the following code will not work with the lab's default **No isolation shared cluster**. You will have to run the cells in this notebook using Serverless or manually delete the pipeline and tables.

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS lab_1_bronze_db.employees_bronze_lab4;
# MAGIC DROP TABLE IF EXISTS lab_2_silver_db.employees_silver_lab4;
# MAGIC DROP VIEW IF EXISTS lab_3_gold_db.employees_by_country_gold_lab4;
# MAGIC DROP VIEW IF EXISTS lab_3_gold_db.salary_by_department_gold_lab4;

# COMMAND ----------

# MAGIC %md
# MAGIC Run the cell below to view and copy the path to your **lab_files** volume. You will need this path when building your pipeline to reference your data source files.
# MAGIC
# MAGIC **NOTE:** You can also navigate to the volume and copy the path using the UI.

# COMMAND ----------

print(f'/Volumes/{DA.catalog_name}/default/lab_files')

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. TO DO: Create the Lakeflow Declarative Pipeline (Steps)
# MAGIC
# MAGIC After you have explored the traditional ETL code to create the tables and views, it's time to modify that syntax to declarative SQL for your new pipeline.
# MAGIC
# MAGIC You will have to complete the following:
# MAGIC
# MAGIC **NOTE:** The solution files can be found in the **4 - Lab Solution Project**. All code is in the one **ingest.sql** file:
# MAGIC
# MAGIC 1. Create a Lakeflow Declarative Pipeline and name it **Lab4 - firstname pipeline project**.
# MAGIC
# MAGIC     - Select your **labuser** catalog  
# MAGIC
# MAGIC     - Select the **default** schema  
# MAGIC
# MAGIC     - Select the **SQL** language  
# MAGIC
# MAGIC     - **NOTE:** The Lakeflow Declarative Pipeline will contain sample files and notebooks. You can exclude the sample files from the pipeline before you run the pipeline.
# MAGIC
# MAGIC
# MAGIC 2. Migrate the ETL code from above (shown below for each step as markdown) into one or more files and folders to organize your pipeline (you can also put everything in a single file if you want).
# MAGIC <br></br>
# MAGIC ##### 2a. Modify the code from above (shown below) to create the **bronze** streaming table by completing the following:
# MAGIC
# MAGIC ```SQL
# MAGIC CREATE OR REPLACE TABLE lab_1_bronze_db.employees_bronze_lab4  -- You will have to modify this to create a streaming table in the pipeline
# MAGIC AS
# MAGIC SELECT 
# MAGIC     *,
# MAGIC     current_timestamp() AS ingestion_time,
# MAGIC     _metadata.file_name as raw_file_name
# MAGIC FROM read_files(                                           -- You will have to modify FROM clause to incrementally read in data
# MAGIC     '/Volumes/' || DA.catalog_name || '/default/lab_files',  -- You will have to modify this path in the pipeline to your specific raw data source
# MAGIC     format => 'CSV',
# MAGIC     header => 'true'
# MAGIC );
# MAGIC ```
# MAGIC
# MAGIC - Modify the `CREATE OR REPLACE TABLE` statement to create a streaming table.  
# MAGIC
# MAGIC - Add the keyword `STREAM` in the `FROM` clause to incrementally ingest data from the delta table.
# MAGIC
# MAGIC - Modify the path in the `FROM` clause to point to your **labuser.default.lab_files** volume path (example: `/Volumes/labuser1234/default/lab_files`). You can statically add the path in the `read_files` function, or use a configuration parameter.
# MAGIC - **NOTE:** You can't use the `DA` object in your path. Remember to add a static path or configuration parameter.
# MAGIC
# MAGIC <br></br>
# MAGIC ##### 2b. Modify the code from above (shown below) to create the **silver** streaming table by completing the following in your pipeline project:
# MAGIC
# MAGIC ```
# MAGIC CREATE OR REPLACE TABLE lab_2_silver_db.employees_silver_lab4 -- You will have to modify this to create a streaming table in the pipeline
# MAGIC AS
# MAGIC SELECT
# MAGIC     EmployeeID,
# MAGIC     FirstName,
# MAGIC     upper(Country) AS Country,
# MAGIC     Department,
# MAGIC     Salary,
# MAGIC     HireDate,
# MAGIC     date_format(HireDate, 'MMMM') AS HireMonthName,
# MAGIC     year(HireDate) AS HireYear, 
# MAGIC     Operation
# MAGIC FROM lab_1_bronze_db.employees_bronze_lab4;                    -- You will have to modify FROM clause to incrementally read in data
# MAGIC ```
# MAGIC
# MAGIC - Modify the `CREATE OR REPLACE TABLE` statement to create a streaming table.  
# MAGIC
# MAGIC - Add the keyword `STREAM` in the `FROM` clause to incrementally ingest data.
# MAGIC
# MAGIC - Add the following data quality expectations:      
# MAGIC ```
# MAGIC CONSTRAINT check_country EXPECT (Country IN ('US','GR')),
# MAGIC CONSTRAINT check_salary EXPECT (Salary > 0),
# MAGIC CONSTRAINT check_null_id EXPECT (EmployeeID IS NOT NULL) ON VIOLATION DROP ROW
# MAGIC
# MAGIC ```
# MAGIC <br></br>
# MAGIC ##### 2c. Replace the `CREATE OR REPLACE VIEW` statement in the two views to create materialized views instead of traditional views in your pipeline project.
# MAGIC
# MAGIC ```
# MAGIC CREATE OR REPLACE VIEW lab_3_gold_db.employees_by_country_gold_lab4 -- You will have to modify this to create a materialized view in the pipeline
# MAGIC AS
# MAGIC SELECT 
# MAGIC     Country,
# MAGIC     count(*) AS TotalEmployees,
# MAGIC     sum(Salary) AS TotalSalary
# MAGIC FROM lab_2_silver_db.employees_silver_lab4
# MAGIC GROUP BY Country;
# MAGIC
# MAGIC
# MAGIC CREATE OR REPLACE VIEW lab_3_gold_db.salary_by_department_gold_lab4  -- You will have to modify this to create a materialized view in the pipeline
# MAGIC AS
# MAGIC SELECT
# MAGIC     Department,
# MAGIC     sum(Salary) AS TotalSalary
# MAGIC FROM lab_2_silver_db.employees_silver_lab4
# MAGIC GROUP BY Department;
# MAGIC
# MAGIC ```
# MAGIC <br></br>
# MAGIC 3. Pipeline configuration requirements:
# MAGIC
# MAGIC - Your Lakeflow Declarative Pipeline should use **Serverless** compute.  
# MAGIC
# MAGIC - Your pipeline should use your **labuser** catalog by default.  
# MAGIC
# MAGIC - Your pipeline should use your **default** schema by default.
# MAGIC
# MAGIC - Make sure your pipeline is including your .sql file only.
# MAGIC
# MAGIC - (OPTIONAL) If using a configuration variable to point to your path make sure it is setup and applied in the `read_files` function.
# MAGIC
# MAGIC <br></br>
# MAGIC 4. When complete, run the pipeline. Troubleshoot any errors.
# MAGIC
# MAGIC <br></br>
# MAGIC
# MAGIC ##### Final Lakeflow Declarative Pipeline Image  
# MAGIC Below is what your final pipeline should look like after the first run with a single CSV file.
# MAGIC
# MAGIC ![Final Lab4 Pipeline](./Includes/images/lab4_solution_graph.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ### LAB SOLUTION (optional)
# MAGIC If you need the solution, you can view the lab solution code in the **4 - Lab Solution Project** folder. You can execute the code below to automatically create the Lakeflow Declarative Pipeline with the necessary configuration settings for your specific lab.
# MAGIC
# MAGIC **NOTE:** After you run the cell, wait 30 seconds for the pipeline to finish creating. Then open one of the files in the **4 - Lab Solution Project** folder to open the new Lakeflow Declarative Pipeline editor.

# COMMAND ----------

create_declarative_pipeline(pipeline_name=f'4 - Lab Solution Project - {DA.catalog_name}', 
                            root_path_folder_name='4 - Lab Solution Project',
                            catalog_name = DA.catalog_name,
                            schema_name = 'default',
                            source_folder_names=['solution'],
                            configuration = {'source':f'/Volumes/{DA.catalog_name}/default/lab_files'})

# COMMAND ----------

# MAGIC %md
# MAGIC ## D. Explore the Streaming Tables and Materialized Views
# MAGIC
# MAGIC After you have created and run your Lakeflow Declarative Pipeline, complete the following tasks to explore your new streaming tables and materialized views.

# COMMAND ----------

# MAGIC %md
# MAGIC 1. In the catalog explorer on the left, expand your **labuser** catalog and expand the following schemas:
# MAGIC    - **lab_1_bronze_db**
# MAGIC    - **lab_2_silver_db**
# MAGIC    - **lab_3_gold_db**
# MAGIC
# MAGIC     You should see the two streaming tables and materialized views within your schemas (if you don't use the solution, you won't have the **_solution** at the end of the streaming tables and materialized views):
# MAGIC
# MAGIC     ![Objects in Schemas](./Includes/images/lab4_solution_schemas.png)

# COMMAND ----------

# MAGIC %md
# MAGIC 2. Run the cell below to view the data in your **labuser.lab_1_bronze_db.employees_bronze_lab4** streaming table. Notice that the first row contains a `null` **EmployeeID**.
# MAGIC
# MAGIC **NOTE:** If you ran the solution pipeline, the streaming table is named **employees_bronze_lab4_solution**.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM lab_1_bronze_db.employees_bronze_lab4;

# COMMAND ----------

# MAGIC %md
# MAGIC 3. Run the cell below to view the data in your **labuser.lab_2_silver_db.employees_silver_lab4** streaming table. Notice that the silver table removed the **EmployeeID** value that contained a `null` using a data quality expectation.
# MAGIC
# MAGIC **NOTE:** If you ran the solution pipeline, the streaming table is named **employees_silver_lab4_solution**.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM lab_2_silver_db.employees_silver_lab4;

# COMMAND ----------

# MAGIC %md
# MAGIC 3. Run the cell below to view the data in your **labuser.lab_3_gold_db.employees_by_country_gold_lab4** materialized view. 
# MAGIC
# MAGIC     **Final Results**
# MAGIC     | Country | TotalCount | TotalSalary |
# MAGIC     |---------|------------|-------------|
# MAGIC     | GR      | 2          | 108000      |
# MAGIC     | US      | 3          | 201000      |
# MAGIC
# MAGIC **NOTE:** If you ran the solution pipeline, the materialized view is named **employees_by_country_gold_lab4_solution**.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM lab_3_gold_db.employees_by_country_gold_lab4
# MAGIC ORDER BY TotalSalary;

# COMMAND ----------

# MAGIC %md
# MAGIC 4. Run the cell below to view the data in your **labuser.lab_3_gold_db.salary_by_department_gold_lab4** materialized view. 
# MAGIC
# MAGIC     **Final Results**
# MAGIC     | Department  | TotalSalary |
# MAGIC     |-------------|-------------|
# MAGIC     | Sales          | 141000      |
# MAGIC     | IT          | 168000      |
# MAGIC
# MAGIC **NOTE:** If you ran the solution pipeline, the materialized view is named **salary_by_department_gold_lab4_solution**.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM lab_3_gold_db.salary_by_department_gold_lab4
# MAGIC ORDER BY TotalSalary;

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. CHALLENGE SCENARIO (OPTIONAL IN LIVE TEACH)
# MAGIC ### Duration: ~10 minutes
# MAGIC
# MAGIC **NOTE:** *If you finish early in a live class, feel free to complete the challenge below. The challenge is optional and most likely won't be completed during the live class. Only continue if your Lakeflow Declarative Pipeline was set up correctly in the previous section by comparing your pipeline to the solution image.*
# MAGIC
# MAGIC **SCENARIO:** In the challenge, you will land a new CSV file in your **lab_files** cloud storage volume and rerun the pipeline to watch the Lakeflow Declarative Pipeline only ingest the new data.

# COMMAND ----------

# MAGIC %md
# MAGIC 1. Run the cell below to copy another file to your **labuser.default.lab_user** volume.
# MAGIC

# COMMAND ----------

LabSetup.copy_file(copy_file = 'employees_2.csv', 
                   to_target_volume = f'/Volumes/{DA.catalog_name}/default/lab_files')

# COMMAND ----------

# MAGIC %md
# MAGIC 2. In the left navigation area, navigate to your **labuser.default.lab_files** volume and expand the volume. Confirm it contains two CSV files: 
# MAGIC     - **employees_1.csv** 
# MAGIC     - **employees_2.csv**
# MAGIC
# MAGIC **NOTE:** You might have to refresh your catalogs if the file is not shown.

# COMMAND ----------

# MAGIC %md
# MAGIC 3. Run the cell below to preview only the new CSV file and view the results. Notice that the new CSV file contains employee information:
# MAGIC
# MAGIC     - Contains 4 rows.  
# MAGIC     - The **Operation** column specifies an action for each employee (e.g., update the record, delete the record, or add a new employee).
# MAGIC
# MAGIC **NOTE:** Don’t worry about the **Operation** column yet. We’ll cover how to capture these specific changes in your data (Change Data Capture) in a later demonstration.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM read_files(                                           
# MAGIC   '/Volumes/' || DA.catalog_name || '/default/lab_files/employees_2.csv',  
# MAGIC   format => 'CSV',
# MAGIC   header => 'true'
# MAGIC );

# COMMAND ----------

# MAGIC %md
# MAGIC 4. Now that you have explored the new CSV file in cloud storage, go back to your Lakeflow Declarative Pipeline and select **Run pipeline**. Notice that the pipeline only read in the new file in cloud storage.
# MAGIC
# MAGIC
# MAGIC ##### Final Lakeflow Declarative Pipeline Image
# MAGIC Below is what your final pipeline should look like after the first run with a single CSV file.
# MAGIC
# MAGIC ![Final Challenge Lab4 DLT Pipeline](./Includes/images/lab4_solution_challenge.png)

# COMMAND ----------

# MAGIC %md
# MAGIC 5. Explore the history of your streaming tables using the Catalog Explorer. Notice that there are two appends to both the **bronze** and **silver** tables.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>