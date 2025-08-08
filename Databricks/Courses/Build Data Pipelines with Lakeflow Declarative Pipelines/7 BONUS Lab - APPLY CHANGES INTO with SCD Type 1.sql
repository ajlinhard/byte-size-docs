-- Databricks notebook source
-- MAGIC %md
-- MAGIC
-- MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
-- MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
-- MAGIC </div>
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC # 7 Bonus Lab - APPLY CHANGES INTO with SCD Type 1
-- MAGIC
-- MAGIC ### Estimated Duration: ~15-20 minutes
-- MAGIC
-- MAGIC #### This is an optional lab that can be completed after class if you're interested in practicing CDC.
-- MAGIC
-- MAGIC
-- MAGIC In this demonstration you will use Change Data Capture (CDC) to detect changes and apply them using SCD Type 1 logic (overwrite, no historical records).
-- MAGIC
-- MAGIC ### Learning Objectives
-- MAGIC
-- MAGIC By the end of this lesson, you will be able to:
-- MAGIC - Use `APPLY CHANGES INTO` to perform Change Data Capture (CDC) using SCD Type 1.

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
-- MAGIC %md
-- MAGIC ## A. Classroom Setup
-- MAGIC
-- MAGIC Run the following cell to configure your working environment for this course.
-- MAGIC
-- MAGIC **NOTE:** The `DA` object is only used in Databricks Academy courses and is not available outside of these courses. It will dynamically create and reference the information needed to run the course.

-- COMMAND ----------

-- MAGIC %run ./Includes/Classroom-Setup-7

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## B. SCENARIO
-- MAGIC
-- MAGIC Your data engineering team wants to build a Lakeflow Declarative Pipeline to maintain a record of current employees without keeping historical data (SCD Type 1). The project has been started, but the final step is to update the silver table with the current employee records that have not yet been completed. 
-- MAGIC
-- MAGIC There are already two files in a cloud storage location that contain information about employees and employee updates.
-- MAGIC
-- MAGIC ### REQUIREMENTS:
-- MAGIC It’s your job to complete the Lakeflow Declarative Pipeline by adding the `APPLY CHANGES INTO` statement to perform SCD Type 1.
-- MAGIC
-- MAGIC Follow the steps below to complete your task.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## C. Explore the Raw Data Source Files

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Run the cell below to programmatically view the files in your `/Volumes/your-lab-catalog-name/default/lab_files` volume. Confirm that you see **employees_1.csv** and **employees_2.csv**.
-- MAGIC
-- MAGIC **NOTE:** You can also manually navigate to your **labuser.default.lab_files** volume and view the files in the volume.
-- MAGIC

-- COMMAND ----------

-- DBTITLE 1,View files in the lab_files volume
-- MAGIC %python
-- MAGIC spark.sql(f'LIST "/Volumes/{DA.catalog_name}/default/lab_files"').display()

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Query the 2 CSV files in that volume. Notice the following:
-- MAGIC
-- MAGIC    - The files contain a list of employees.
-- MAGIC
-- MAGIC    - The **employees_1.csv** contains the initial employees.  
-- MAGIC    
-- MAGIC    - The **employees_2.csv** contains an update, a delete, and a new employee.
-- MAGIC
-- MAGIC    - The **Operation** column provides information about the action for each record (new employee, update employee information, or delete employee).
-- MAGIC
-- MAGIC    - The **ProcessDate** column indicates when the records were processed (acts as a sequence column).
-- MAGIC
-- MAGIC    - In total, there are 10 rows.
-- MAGIC
-- MAGIC       - There are two duplicate **EmployeeID** values:
-- MAGIC         - **EmployeeID 1** – Sophia was an employee, then should be deleted.
-- MAGIC         - **EmployeeID 3** – Liam received a bonus, and his **Salary** needs to be updated.
-- MAGIC         
-- MAGIC       - **Employee 6 & 7** - New employees from the **employees_2.csv** file.

-- COMMAND ----------

-- DBTITLE 1,View the volume CSV files
SELECT 
  *,
  _metadata.file_name as source_file
FROM read_files(
  '/Volumes/' || DA.catalog_name || '/default/lab_files',
  format => 'CSV'
)
ORDER BY EmployeeID, ProcessDate DESC;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. Looking at the output from above, our final table after applying SCD Type 1 on the two files should:
-- MAGIC
-- MAGIC    - Contain 6 rows of data:
-- MAGIC       - remove the **EmployeeID** with a `null` value (removed with a data quality expectation)
-- MAGIC       - delete **EmployeeID** 1
-- MAGIC
-- MAGIC    - **EmployeeID 3** should have a current salary of 100,000 and only one row of data.
-- MAGIC
-- MAGIC    - **EmployeeID 5 & 6** are new employees from **employees_2.csv** file.
-- MAGIC
-- MAGIC    - No historical data should be tracked.
-- MAGIC
-- MAGIC <br></br>
-- MAGIC
-- MAGIC **FINAL TABLE OUTPUT**
-- MAGIC | EmployeeID | FirstName | Country | Department | Salary | HireDate   | ProcessDate |
-- MAGIC |------------|-----------|---------|------------|--------|------------|-------------|
-- MAGIC | 2          | Nikos     | GR      | IT         | 55000  | 2025-04-10 | 2025-06-05  |
-- MAGIC | 3          | Liam      | US      | Sales      | **100000** | 2025-05-03 | **2025-06-22**  |
-- MAGIC | 4          | Elena     | GR      | IT         | 53000  | 2025-06-04 | 2025-06-05  |
-- MAGIC | 5          | James     | US      | IT         | 60000  | 2025-06-05 | 2025-06-05  |
-- MAGIC | 6          | Emily     | US      | Enablement | 80000  | 2025-06-09 | **2025-06-22**  |
-- MAGIC | 7          | Yannis    | GR      | HR         | 70000  | 2025-06-20 | **2025-06-22**  |
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## D. TO DO: Complete the Pipeline with SCD Type 1

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Run the cell below to create your starter Lakeflow Declarative Pipeline for this lab. The pipeline will set the following for you:
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

-- MAGIC %python
-- MAGIC create_declarative_pipeline(pipeline_name=f'7 - CDC Lab Starter Project - {DA.catalog_name}', 
-- MAGIC                             root_path_folder_name='7 - CDC Lab Starter Project',
-- MAGIC                             catalog_name = DA.catalog_name,
-- MAGIC                             schema_name = 'default',
-- MAGIC                             source_folder_names=['cdc_type_1_pipeline'],
-- MAGIC                             configuration = {'source':f'/Volumes/{DA.catalog_name}/default/lab_files'})

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Complete the following steps to open the starter Lakeflow Declarative Pipeline project for this lab:
-- MAGIC
-- MAGIC    a. Click the folder icon ![Folder](./Includes/images/folder_icon.png) in the left navigation panel.
-- MAGIC
-- MAGIC    b. In the **Build Data Pipelines with Lakeflow Declarative Pipelines** folder, find the **7 - CDC Lab Starter Project** folder. 
-- MAGIC    
-- MAGIC    c. Right-click and select **Open in a new tab**.
-- MAGIC
-- MAGIC    d. In the new tab you should see the folder: **cdc_type_1_pipeline**. 
-- MAGIC
-- MAGIC    e. Open the **cdc_type_1_pipeline** folder and select the **cdc_employees.sql** notebook.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### TO DO: Review the code in the cdc_employees.sql file and complete the `APPLY CHANGES INTO STATEMENT` to perform SCD Type 1.
-- MAGIC    
-- MAGIC    - For simplicity in training, all code for the pipeline is in one file **cdc_employees.sql**.
-- MAGIC
-- MAGIC    - Walk through the **cdc_employees.sql** file and read the comments.
-- MAGIC
-- MAGIC    - The **bronze** and **silver** table code is completed for you. You just need to complete the `APPLY CHANGES INTO STATEMENT`.
-- MAGIC
-- MAGIC    - If you need the solution to the pipeline you can view it in the **7 - CDC Lab Solution Project** folder.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ##### TROUBLESHOOT
-- MAGIC    **NOTE:** If you open the **cdc_employees.sql** file and it does not open up the new editor, that is because that folder is not associated with a Lakeflow Declarative Pipeline. Please make sure to run the previous cell to associate the folder with a pipeline and try again.
-- MAGIC
-- MAGIC    **WARNING:** If you get the following warning when opening the **cdc_employees.sql** file: 
-- MAGIC
-- MAGIC    ```pipeline you are trying to access does not exist or is inaccessible. Please verify the pipeline ID, request access or detach this file from the pipeline.``` 
-- MAGIC
-- MAGIC    Simply refresh the page and/or reselect the notebook.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## E. Explore Your CDC SCD Type 1 Streaming Table
-- MAGIC
-- MAGIC After you have completed the `APPLY CHANGES INTO` statement in the **cdc_employees.sql** file, compare your results to the solution image below.
-- MAGIC
-- MAGIC **FINAL PIPELINE RUN**
-- MAGIC
-- MAGIC ![Lab 7 Pipeline Run](./Includes/images/lab_7_pipeline_run.png)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Run the cell below to view the data in your **lab_2_silver_db.current_employees_silver_demo7** streaming table that applied SCD Type 1, and compare it to the solution below.
-- MAGIC
-- MAGIC     Notice with SCD Type 1 no historical data is kept.
-- MAGIC
-- MAGIC **FINAL TABLE SOLUTION**
-- MAGIC | EmployeeID | FirstName | Country | Department | Salary | HireDate   | ProcessDate |
-- MAGIC |------------|-----------|---------|------------|--------|------------|-------------|
-- MAGIC | 2          | Nikos     | GR      | IT         | 55000  | 2025-04-10 | 2025-06-05  |
-- MAGIC | 3          | Liam      | US      | Sales      | **100000** | 2025-05-03 | **2025-06-22**  |
-- MAGIC | 4          | Elena     | GR      | IT         | 53000  | 2025-06-04 | 2025-06-05  |
-- MAGIC | 5          | James     | US      | IT         | 60000  | 2025-06-05 | 2025-06-05  |
-- MAGIC | 6          | Emily     | US      | Enablement | 80000  | 2025-06-09 | **2025-06-22**  |
-- MAGIC | 7          | Yannis    | GR      | HR         | 70000  | 2025-06-20 | **2025-06-22**  |
-- MAGIC
-- MAGIC **NOTE**: If you ran the solution pipeline, the streaming table is named **current_employees_silver_demo7_solution**

-- COMMAND ----------

SELECT *
FROM lab_2_silver_db.current_employees_silver_demo7
ORDER BY EmployeeID

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## F. Lab Solution (OPTIONAL)
-- MAGIC If you want to run the solution, you can execute the cell below to create a pipeline using the **7 - CDC Lab Solution Project** project folder.
-- MAGIC
-- MAGIC Each table in this solution pipeline will end with **_solution**.

-- COMMAND ----------

-- MAGIC %python
-- MAGIC create_declarative_pipeline(pipeline_name=f'7 - CDC Lab Solution Project - {DA.catalog_name}', 
-- MAGIC                             root_path_folder_name='7 - CDC Lab Solution Project',
-- MAGIC                             catalog_name = DA.catalog_name,
-- MAGIC                             schema_name = 'default',
-- MAGIC                             source_folder_names=['cdc_type_1_pipeline'],
-- MAGIC                             configuration = {'source':f'/Volumes/{DA.catalog_name}/default/lab_files'})

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## G. CHALLENGE SCENARIO
-- MAGIC ### Duration: ~10 minutes
-- MAGIC
-- MAGIC **NOTE:** *If you finish early in a live class, feel free to complete the challenge below. The challenge is optional and most likely won't be completed during the live class. Only continue if your Lakeflow Declarative Pipeline pipeline was set up correctly in the previous section by comparing your pipeline to the solution image.*
-- MAGIC
-- MAGIC **SCENARIO:** In the challenge, you will land a new CSV file in your **lab_files** cloud storage volume and rerun the pipeline to watch the Lakeflow Declarative Pipeline perform CDC SCD Type 1 on the new data.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Run the cell below to land another file in your **lab_files** cloud storage location.

-- COMMAND ----------

-- MAGIC %python
-- MAGIC LabSetup.copy_file(copy_file = 'employees_3.csv', 
-- MAGIC                    to_target_volume = f'/Volumes/{DA.catalog_name}/default/lab_files')

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Query the **employees_3.csv** file. Notice the following:
-- MAGIC
-- MAGIC    - **EmployeeID** values **2** and **6** need to be removed.
-- MAGIC
-- MAGIC    - **EmployeeID 8** is a new employee in our company.
-- MAGIC

-- COMMAND ----------

SELECT 
  *,
  _metadata.file_name as source_file
FROM read_files(
  '/Volumes/' || DA.catalog_name || '/default/lab_files/employees_3.csv',
  format => 'CSV'
);

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. Go back to your pipeline and select **Run pipeline**. Examine the pipeline run. Confirm it shows the following:
-- MAGIC
-- MAGIC ![Lab 7 Challenge Run](./Includes/images/lab_7_challenge_solution.png)
-- MAGIC ![Lab 7 Challenge Run](./Includes/images/lab4_challenge_metrics.png)
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 4. Run the cell below to query the table **lab_2_silver_db.current_employees_silver_demo7** and view the results. Notice that:
-- MAGIC
-- MAGIC    - The two employees (**EmployeeID** 2 and 6) were deleted.
-- MAGIC
-- MAGIC    - **EmployeeID 8** was added.
-- MAGIC
-- MAGIC    - No historical data is kept with SCD Type 1.
-- MAGIC
-- MAGIC     **NOTE:** If you ran the solution pipeline, the streaming table is named **lab_2_silver_db.current_employees_silver_demo7_solution**.
-- MAGIC
-- MAGIC
-- MAGIC     **FINAL TABLE**
-- MAGIC | EmployeeID | FirstName  | Country | Department | Salary  | HireDate   | ProcessDate |
-- MAGIC |------------|------------|---------|------------|---------|------------|-------------|
-- MAGIC | 3          | Liam       | US      | Sales      | 100000  | 2025-05-03 | 2025-06-22  |
-- MAGIC | 4          | Elena      | GR      | IT         | 53000   | 2025-06-04 | 2025-06-05  |
-- MAGIC | 5          | James      | US      | IT         | 60000   | 2025-06-05 | 2025-06-05  |
-- MAGIC | 7          | Yannis     | GR      | HR         | 70000   | 2025-06-20 | 2025-06-22  |
-- MAGIC | 8          | Panagiotis | GR      | Enablement | 90000   | 2025-07-01 | 2025-07-22  |

-- COMMAND ----------

SELECT *
FROM lab_2_silver_db.current_employees_silver_demo7
ORDER BY EmployeeID;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC
-- MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
-- MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
-- MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
-- MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>