-- Databricks notebook source
-- MAGIC %md
-- MAGIC
-- MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
-- MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
-- MAGIC </div>
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC # 2 - Developing a Simple Pipeline
-- MAGIC
-- MAGIC In this demonstration, we will create a simple Lakeflow Declarative Pipeline project using the new **ETL Pipeline multi-file editor** with declarative SQL.
-- MAGIC
-- MAGIC
-- MAGIC ### Learning Objectives
-- MAGIC
-- MAGIC By the end of this lesson, you will be able to:
-- MAGIC - Describe the SQL syntax used to create a Lakeflow Declarative Pipeline pipeline.
-- MAGIC - Navigate the Lakeflow Declarative Pipeline ETL Pipeline multi-file editor to modify pipeline settings and ingest the raw data source file(s).
-- MAGIC - Create, execute and monitor a Lakeflow Declarative Pipeline pipeline.

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
-- MAGIC Run the following cell to configure your working environment for this course.
-- MAGIC
-- MAGIC This cell will also reset your `/Volumes/dbacademy/ops/labuser/` volume with the JSON files to the starting point, with one JSON file in each volume.
-- MAGIC
-- MAGIC **NOTE:** The `DA` object is only used in Databricks Academy courses and is not available outside of these courses. It will dynamically create and reference the information needed to run the course.

-- COMMAND ----------

-- MAGIC %run ./Includes/Classroom-Setup-2

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## B. Developing and Running a Lakeflow Declarative  Pipeline with the ETL Pipeline Multi-File Editor
-- MAGIC
-- MAGIC This course includes a simple, pre-configured Lakeflow Declarative Pipeline to explore and modify. In this section, we will:
-- MAGIC
-- MAGIC - Explore the ETL Pipeline multi-file editor and the declarative SQL syntax  
-- MAGIC - Modify pipeline settings  
-- MAGIC - Run the Lakeflow Declarative Pipeline and explore the streaming tables and materialized view.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Run the cell below and **copy the path** from the output cell to your **dbacademy.ops.labuser** volume. You will need this path when modifying your pipeline settings. 
-- MAGIC
-- MAGIC    This volume path contains the **orders**, **status** and **customer** directories, which contain the raw JSON files.
-- MAGIC
-- MAGIC    **EXAMPLE PATH**: `/Volumes/dbacademy/ops/labuser1234_5678@vocareum.com`

-- COMMAND ----------

-- DBTITLE 1,Path to data source files
-- MAGIC %python
-- MAGIC print(DA.paths.working_dir)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. In this course we have starter files for you to use in your pipeline. This demonstration uses the folder **2 - Developing a Simple Pipeline Project**. To create a pipeline and add existing assets to associate it with code files already available in your Workspace (including Git folders) complete the following:
-- MAGIC
-- MAGIC    a. In the left navigation bar, select the **Folder** ![Folder Icon](./Includes/images/folder_icon.png) icon to open the Workspace navigation.
-- MAGIC
-- MAGIC    b. Navigate to the **Build Data Pipelines with Lakeflow Declarative Pipelines** folder (you may already be there).
-- MAGIC
-- MAGIC    c. **(PLEASE READ)** For ease of use, open this same notebook in a separate tab:
-- MAGIC
-- MAGIC     - Right-click the notebook in the left navigation.
-- MAGIC
-- MAGIC     - Select **Open in a New Tab**.
-- MAGIC
-- MAGIC    d. In the new tab, click the **three-dot (ellipsis) icon** ![Ellipsis Icon](./Includes/images/ellipsis_icon.png) in the folder navigation bar.
-- MAGIC
-- MAGIC    e. Select **Create** → **ETL Pipeline**.
-- MAGIC
-- MAGIC    f. Complete the pipeline creation page with the following:
-- MAGIC
-- MAGIC     - **Name**: `Name-your-pipeline-using-this-notebook-name-add-your-first-name` 
-- MAGIC     - **Default catalog**: Select your **labuser** catalog  
-- MAGIC     - **Default schema**: Select your **default** schema (database)
-- MAGIC
-- MAGIC    g. Select **Add existing assets**. In the popup, complete the following:
-- MAGIC
-- MAGIC     - **Pipeline root folder**: Select the **2 - Developing a Simple DLT Pipeline Project** folder (`/Workspace/Users/your-lab-user-name/build-data-pipelines-with-dlt-3.0.0/Build Data Pipelines with DLT/2 - Developing a Simple DLT Pipeline Project`)
-- MAGIC
-- MAGIC     - **Source code paths**: Within the same root folder as above, select the **orders** folder (`/Workspace/Users/your-lab-user-name/build-data-pipelines-with-dlt-3.0.0/Build Data Pipelines with DLT/2 - Developing a Simple DLT Pipeline Project/orders`)
-- MAGIC
-- MAGIC    h. This will create a pipeline and associate the correct files for this demonstration.
-- MAGIC
-- MAGIC **Example**
-- MAGIC
-- MAGIC ![Example Demo 2](./Includes/images/demo02_existing_assets.png)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. In the new window, select the **orders_pipeline.sql** file and follow the instructions in the file. Leave this notebook as you will use it later.
-- MAGIC
-- MAGIC ![Orders File Directions](./Includes/images/demo02_select_orders_sql_file.png)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## C. Add a New File to Cloud Storage
-- MAGIC
-- MAGIC 1. After exploring and executing the pipeline by following the instructions in the **`orders_pipeline.sql`** file, run the cell below to add a new JSON file (**01.json**) to your volume at:  `/Volumes/dbacademy/ops/labuser-your-id/orders`.
-- MAGIC
-- MAGIC    **NOTE:** If you receive the error `name 'DA' is not defined`, you will need to rerun the classroom setup script at the top of this notebook to create the `DA` object. This is required to correctly reference the path and successfully copy the file.

-- COMMAND ----------

-- DBTITLE 1,Add a new JSON file to the data source
-- MAGIC %python
-- MAGIC copy_files('/Volumes/dbacademy_retail/v01/retail-pipeline/orders/stream_json', 
-- MAGIC            f'{DA.paths.working_dir}/orders', 
-- MAGIC            n = 2)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Complete the following steps to view the new file in your volume:
-- MAGIC
-- MAGIC    a. Select the **Catalog** icon ![Catalog Icon](./Includes/images/catalog_icon.png) from the left navigation pane.  
-- MAGIC    
-- MAGIC    b. Expand your **dbacademy.ops.labuser** volume.  
-- MAGIC    
-- MAGIC    c. Expand the **orders** directory. You should see two files in your volume: **00.json** and **01.json**.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. Run the cell below to view the data in the new **/orders/01.json** file. Notice the following:
-- MAGIC
-- MAGIC    - The **01.json** file contains new orders.  
-- MAGIC    - The **01.json** file has 25 rows.
-- MAGIC

-- COMMAND ----------

-- DBTITLE 1,Preview the 01.json file
-- MAGIC %python
-- MAGIC spark.sql(f'''
-- MAGIC   SELECT *
-- MAGIC   FROM json.`{DA.paths.working_dir}/orders/01.json`
-- MAGIC ''').display()

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 4. Go back to the **orders_pipeline.sql** file and select **Run Pipeline** to execute your ETL pipeline again with the new file (Step 13).  
-- MAGIC
-- MAGIC    Watch the pipeline run and notice that only 25 rows are added to the bronze and silver tables. 
-- MAGIC    
-- MAGIC    This happens because the pipeline has already processed the first **00.json** file (174 rows), and it is now only reading the new **01.json** file (25 rows), appending the rows to the streaming tables, and recomputing the materialized view with the latest data.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## D. Exploring Your Streaming Tables

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. View the new streaming tables and materialized view in your catalog. Complete the following:
-- MAGIC
-- MAGIC    a. Select the catalog icon ![Catalog Icon](./Includes/images/catalog_icon.png) in the left navigation pane.
-- MAGIC
-- MAGIC    b. Expand your **labuser** catalog.
-- MAGIC
-- MAGIC    c. Expand the schemas **1_bronze_db**, **2_silver_db**, and **3_gold_db**. Notice that the two streaming tables and materialized view are correctly placed in your schemas.
-- MAGIC
-- MAGIC       - **labuser.1_bronze_db.orders_bronze_demo2**
-- MAGIC
-- MAGIC       - **labuser.2_silver_db.orders_silver_demo2**
-- MAGIC
-- MAGIC       - **labuser.3_gold_db.orders_by_date_gold_demo2**

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Run the cell below to view the data in the **labuser.1_bronze_db.orders_bronze_demo2** table. Before you run the cell, how many rows should this streaming table have?
-- MAGIC
-- MAGIC    Notice that the following:
-- MAGIC       - The table contains 199 rows (**00.json** had 174 rows, and **01.json** had 25 rows).
-- MAGIC       - In the **source_file** column you can see the exact file the rows were ingested from.
-- MAGIC       - In the **processing_time** column you can see the exact time the rows were ingested.

-- COMMAND ----------

-- DBTITLE 1,View the streaming table
SELECT *
FROM 1_bronze_db.orders_bronze_demo2;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. Complete the following steps to view the history of the **orders_bronze_demo2** streaming table:
-- MAGIC
-- MAGIC    a. Select the **Catalog** icon ![Catalog Icon](./Includes/images/catalog_icon.png) in the left navigation pane.  
-- MAGIC    
-- MAGIC    b. Expand the **labuser.01_bronze_db** schema.  
-- MAGIC    
-- MAGIC    c. Click the three-dot (ellipsis) icon next to the **orders_bronze_demo2** table.  
-- MAGIC    
-- MAGIC    d. Select **Open in Catalog Explorer**.  
-- MAGIC    
-- MAGIC    e. In the Catalog Explorer, select the **History** tab. Notice an error is returned because viewing the history of a streaming table requires **SHARED_COMPUTE**. In our labs we use a **DEDICATED (formerly single user)** cluster.
-- MAGIC
-- MAGIC    f. Above your catalogs on the left select your compute cluster and change it to the provided **shared_warehouse**.
-- MAGIC
-- MAGIC    ![Change Compute](./Includes/images/change_compute.png)  
-- MAGIC    
-- MAGIC    g. Go back and look at the last two versions of the table. Notice the following:  
-- MAGIC    
-- MAGIC       - In the **Operation** column, the last two updates were **STREAMING UPDATE**.  
-- MAGIC       
-- MAGIC       - Expand the **Operation Parameters** values for the last two updates. Notice both use `"outputMode": "Append"`.  
-- MAGIC       
-- MAGIC       - Find the **Operation Metrics** column. Expand the values for the last two updates. Observe the following:
-- MAGIC       
-- MAGIC          - It displays various metrics for the streaming update: **numRemovedFiles, numOutputRows, numOutputBytes, and numAddedFiles**.  
-- MAGIC          
-- MAGIC          - In the `numOutputRows` values, 174 rows were added in the first update, and 25 rows in the second.
-- MAGIC    
-- MAGIC    h. Close the Catalog Explorer.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## E. Viewing Lakeflow Declarative Pipelines with the Pipelines UI
-- MAGIC
-- MAGIC After exploring and creating your pipeline using the **orders_pipeline.sql** file in the steps above, you can view the pipeline(s) you created in your workspace via the **Pipelines** UI.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Complete the following steps to view the pipeline you created:
-- MAGIC
-- MAGIC    a. In the main applications navigation pane on the far left (you may need to expand it by selecting the ![Expand Navigation Pane](./Includes/images/expand_main_navigation.png) icon at the top left of your workspace) right-click on **Pipelines** and select **Open Link in a New Tab**.
-- MAGIC
-- MAGIC    b. This should take you to the pipelines you have created. You should see your **2 - Developing a Simple Pipeline Project - labuser** pipeline.
-- MAGIC
-- MAGIC    c. Select your **2 - Developing a Simple Pipeline Project - labuser**. Here, you can use the UI to modify the pipeline.
-- MAGIC
-- MAGIC    d. Select the **Settings** button at the top. This will take you to the settings within the UI.
-- MAGIC
-- MAGIC    e. Select **Schedule** to schedule the pipeline. Select **Cancel**, we will learn how to schedule the pipeline later.
-- MAGIC
-- MAGIC    f. Under your pipeline name, select the drop-down with the time date stamp. Here you can view the **Pipeline graph** and other metrics for each run of the pipeline.
-- MAGIC
-- MAGIC    g. Close the pipeline UI tab you opened.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Additional Resources
-- MAGIC
-- MAGIC - [Lakeflow Declarative Pipelines](https://docs.databricks.com/aws/en/dlt/) documentation.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC
-- MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
-- MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
-- MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
-- MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>