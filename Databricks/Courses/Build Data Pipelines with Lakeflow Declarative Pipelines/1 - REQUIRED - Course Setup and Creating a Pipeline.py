# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # 1 - REQUIRED - Course Setup and Creating a Pipeline
# MAGIC
# MAGIC In this demo, we'll set up the course environment, explore its components, build a traditional ETL pipeline using JSON files, and learn how to create a sample Lakeflow Declarative Pipeline.
# MAGIC
# MAGIC ### Learning Objectives
# MAGIC
# MAGIC By the end of this lesson, you will be able to:
# MAGIC - Efficiently navigate the Workspace to locate course catalogs, schemas, and source files.
# MAGIC - Create and a Lakeflow Declarative Pipeline using the Workspace and the Pipeline UI.
# MAGIC
# MAGIC
# MAGIC ### IMPORTANT - PLEASE READ!
# MAGIC - **REQUIRED** - This notebook is required for all users to run. If you do not run this notebook, you will be missing the necessary files and schemas required for the rest of the course.

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

# MAGIC %run ./Includes/Classroom-Setup-1-setup-REQUIRED

# COMMAND ----------

# MAGIC %md
# MAGIC ## B. Explore the Lab Environment
# MAGIC
# MAGIC Explore the raw data source files, catalogs, and schema in the course lab environment.

# COMMAND ----------

# MAGIC %md
# MAGIC 1. Complete these steps to explore your user catalog and schemas you will be using in this course:
# MAGIC
# MAGIC    - a. Select the **Catalog** icon ![Catalog Icon](./Includes/images/catalog_icon.png) in the left navigation bar.
# MAGIC
# MAGIC    - b. You should see your unique catalog, named something like **labuser1234_56789**. You will use this catalog throughout the course.
# MAGIC
# MAGIC    - c. Expand your **labuser** catalog. It should contain the following schemas:
# MAGIC      - **1_bronze_db**
# MAGIC      - **2_silver_db**
# MAGIC      - **3_gold_db**
# MAGIC      - **default**

# COMMAND ----------

# MAGIC %md
# MAGIC 2. Complete the following steps to view where our streaming raw source files are coming from:
# MAGIC
# MAGIC    a. Select the **Catalog** icon ![Catalog Icon](./Includes/images/catalog_icon.png) in the left navigation bar.
# MAGIC
# MAGIC    b. Expand the **dbacademy** catalog.
# MAGIC
# MAGIC    c. Expand the **ops** schema and then **Volumes**.
# MAGIC
# MAGIC    d. Expand your **labuser@vocareum** volume. You should notice that your volume contains three folders:
# MAGIC    - **customers**
# MAGIC    - **orders**
# MAGIC    - **status**
# MAGIC
# MAGIC    e. Expand each folder and notice that each cloud storage location contains a single JSON file to start with.

# COMMAND ----------

# MAGIC %md
# MAGIC 3. To easily reference this volume path (`/Volumes/dbacademy/ops/your-labuser-name`) throughout the course, you can use the:
# MAGIC - The python `DA.paths.working_dir` variable
# MAGIC - The SQL `DA.paths_working_dir` variable
# MAGIC
# MAGIC    Run the cells below and confirm that the path points to your volume.
# MAGIC
# MAGIC    **Example:** `/Volumes/dbacademy/ops/labuser1234_5678@vocareum`

# COMMAND ----------

## With Python
print(DA.paths.working_dir)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- With SQL
# MAGIC values(DA.paths_working_dir)

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Build a Traditional ETL Pipeline

# COMMAND ----------

# MAGIC %md
# MAGIC 1. Query the raw JSON file(s) in your `/Volumes/dbacademy/ops/your-labuser-name/orders` volume to preview the data. 
# MAGIC
# MAGIC       Notice that the JSON file is displayed ingested into tabular form using the `read_files` function. Take note of the following:
# MAGIC
# MAGIC     a. The **orders** JSON file contains order data for a company.
# MAGIC    
# MAGIC     b. The one JSON file in your **/orders** volume (**00.json**) contains 174 rows. Remember that number for later.

# COMMAND ----------

# DBTITLE 1,View the orders JSON file
spark.sql(f'''
          SELECT * 
          FROM json.`{DA.paths.working_dir}/orders`
          ''').display()

# COMMAND ----------

# MAGIC %md
# MAGIC 2. Traditionally, you would build an ETL pipeline by reading all of the files within the cloud storage location each time the pipeline runs. As data scales, this method becomes inefficient, more expensive, and time-consuming.
# MAGIC
# MAGIC    For example, you would write code like below.
# MAGIC
# MAGIC    **NOTES:** 
# MAGIC    - The tables and views will be written to your **labuser.default** schema (database).
# MAGIC    - Knowledge of the Databricks `read_files` function is prerequisite for this course.

# COMMAND ----------

# DBTITLE 1,Traditional ETL
# MAGIC %sql
# MAGIC -- JSON -> Bronze
# MAGIC -- Read ALL files from your working directory each time the query is executed
# MAGIC CREATE OR REPLACE TABLE default.orders_bronze
# MAGIC AS 
# MAGIC SELECT 
# MAGIC   *,
# MAGIC   current_timestamp() AS processing_time,
# MAGIC   _metadata.file_name AS source_file
# MAGIC FROM read_files(
# MAGIC     DA.paths_working_dir || "/orders", 
# MAGIC     format =>"json");
# MAGIC
# MAGIC
# MAGIC -- Bronze -> Silver
# MAGIC -- Read the entire bronze table each time the query is executed
# MAGIC CREATE OR REPLACE TABLE default.orders_silver
# MAGIC AS 
# MAGIC SELECT 
# MAGIC   order_id,
# MAGIC   timestamp(order_timestamp) AS order_timestamp, 
# MAGIC   customer_id,
# MAGIC   notifications
# MAGIC FROM default.orders_bronze;   
# MAGIC
# MAGIC
# MAGIC -- Silver -> Gold
# MAGIC -- Aggregate the silver each time the query is executed.
# MAGIC CREATE OR REPLACE VIEW default.orders_by_date_vw     
# MAGIC AS 
# MAGIC SELECT 
# MAGIC   date(order_timestamp) AS order_date, 
# MAGIC   count(*) AS total_daily_orders
# MAGIC FROM default.orders_silver                               
# MAGIC GROUP BY date(order_timestamp);

# COMMAND ----------

# MAGIC %md
# MAGIC 3. Run the code in the cells to view the **orders_bronze** and **orders_silver** tables, and the **orders_by_date_vw** view. Explore the results.

# COMMAND ----------

# DBTITLE 1,Preview the bronze table
# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM default.orders_bronze
# MAGIC LIMIT 5;

# COMMAND ----------

# DBTITLE 1,Preview the silver table
# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM default.orders_silver
# MAGIC LIMIT 5;

# COMMAND ----------

# DBTITLE 1,Preview the gold view
# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM default.orders_by_date_vw
# MAGIC LIMIT 5;

# COMMAND ----------

# MAGIC %md
# MAGIC ### Considerations
# MAGIC
# MAGIC - As JSON files are added to the volume in cloud storage, your **bronze table** code will read **all** of the files each time it executes, rather than reading only new rows of raw data. As the data grows, this can become inefficient and costly.
# MAGIC
# MAGIC - The **silver table** code will always read all the rows from the bronze table to prepare the silver table. As the data grows, this can also become inefficient and costly.
# MAGIC
# MAGIC - The traditional view, **orders_by_date_vw**, executes each time it is called. As the data grows, this can become inefficient.
# MAGIC
# MAGIC - To check data quality as new rows are added, additional code is needed to identify any values that do not meet the required conditions.
# MAGIC
# MAGIC - Monitoring the pipeline for each run is a challenge.
# MAGIC
# MAGIC - There is no simple user interface to explore, monitor, or fix issues everytime the code runs.
# MAGIC
# MAGIC ### We can automatically process data incrementally, manage infrastructure, monitor, observe, optimize, and view this ETL pipeline by converting this to use **Lakeflow Declarative Pipelines**!

# COMMAND ----------

# MAGIC %md
# MAGIC ## D. Get Started Creating a Lakeflow Declarative Pipeline Using the New Multi-File Editor
# MAGIC
# MAGIC In this section, we’ll show you how to start creating a Lakeflow Declarative Pipeline using the new Multi-File Editor. We won’t run or modify the pipeline just yet!
# MAGIC
# MAGIC There are a few different ways to create your pipeline. Let’s explore these methods.

# COMMAND ----------

# MAGIC %md
# MAGIC 1. First, complete the following steps to enable the new **ETL Pipeline Multi-File Editor**:
# MAGIC
# MAGIC    **NOTE:** This is being updated and how to enable it might change slightly moving forward.
# MAGIC
# MAGIC    a. In the top-right corner, select your user icon ![User Lab Icon](./Includes/images/user_lab_circle_icon.png).
# MAGIC
# MAGIC    b. Right-click on **Settings** and select **Open in New Tab**.
# MAGIC
# MAGIC    c. Select **Developer**.
# MAGIC
# MAGIC    d. Scroll to the bottom and enable **ETL Pipeline Multi-File Editor** if it's not enabled and Click **Enable tabs for notebooks and files**.
# MAGIC
# MAGIC    ![Multi File Editor Option](./Includes/images/multi-file-editor-option.png)
# MAGIC
# MAGIC    e. Refresh your browser page to enable the option you turned on.

# COMMAND ----------

# MAGIC %md
# MAGIC ### D1. Create a Lakeflow Declarative Pipeline Using the File Explorer
# MAGIC 1. Complete the following steps to create a Lakeflow Declarative Pipeline using the left navigation pane:
# MAGIC
# MAGIC    a. In the left navigation bar, select the **Folder** ![Folder Icon](./Includes/images/folder_icon.png) icon to open the Workspace navigation.
# MAGIC
# MAGIC    b. Navigate to the **Build Data Pipelines with Lakeflow Declarative Pipelines** folder (you are most likely already there).
# MAGIC
# MAGIC    c. (**PLEASE READ**) To complete this demonstration, it'll be easier to open this same notebook in another tab to follow along with these instructions. Right click on the notebook **1 - REQUIRED - Course Setup and Creating a Pipeline** and select **Open in a New Tab**.
# MAGIC
# MAGIC    d. In the other tab select the three ellipsis icon ![Ellipsis Icon](./Includes/images/ellipsis_icon.png) in the folder navigation bar.
# MAGIC
# MAGIC    e. Select **Create** -> **ETL Pipeline**:
# MAGIC       - If you have not enabled the new **ETL Pipeline Multi-File Editor** a pop-up might appear asking you to enable the new editor. Select **Enable** here or complete the previous step.
# MAGIC
# MAGIC       </br>
# MAGIC       
# MAGIC       - Then use the following information:
# MAGIC
# MAGIC          - **Name**: `yourfirstname-my-pipeline-project`
# MAGIC
# MAGIC          - **Default catalog**: Select your **labuser** catalog
# MAGIC
# MAGIC          - **Default schema**: Select your **default** schema (database)
# MAGIC
# MAGIC          - Select **Start with sample in SQL**
# MAGIC
# MAGIC          The project will open up in the pipeline editor and look like the following:
# MAGIC
# MAGIC       ![Pipeline Editor](./Includes/images/new_pipeline_editor_sample.png)
# MAGIC
# MAGIC    f. This will open your Lakeflow Declarative Pipeline within the **ETL Pipeline multi-file editor**. By default, the project creates multiple folders and sample files for you as a starter. You can use this sample folder structure or create your own. Notice the following in the pipeline editor:
# MAGIC
# MAGIC       - The Lakeflow Declarative Pipeline is located within the **Pipeline** tab.
# MAGIC
# MAGIC       - Here, you start with a sample project and folder structure.
# MAGIC
# MAGIC       - To navigate back to all your files and folders, select **All Files**.
# MAGIC
# MAGIC       - We will explore the pipeline editor and running a pipeline in the next demonstration.
# MAGIC
# MAGIC    g. Close the link with the sample pipeline.

# COMMAND ----------

# MAGIC %md
# MAGIC ### D2. Create a Lakeflow Declarative Pipeline Using the Pipeline UI
# MAGIC 1. You can also create a Lakeflow Declarative Pipeline using the far-left main navigation bar by completing the following steps:
# MAGIC
# MAGIC    a. On the far-left navigation bar, right-click **Pipelines** and select **Open Link in New Tab**.
# MAGIC
# MAGIC    b. Find the blue **Create** button and select it.
# MAGIC
# MAGIC    c. Select **ETL pipeline**.
# MAGIC
# MAGIC    d. The same **Create pipeline** pop-up appears as before. 
# MAGIC
# MAGIC    e. Here select **Add existing assets**. 
# MAGIC
# MAGIC    f. The **Add existing assets** button enables you to select a folder with pipeline assets. This option will enable you to associate this new pipeline with code files already available in your Workspace, including Git folders.
# MAGIC
# MAGIC    ![Existing Assets](./Includes/images/existing_assets.png)
# MAGIC
# MAGIC    g. You can close out of the pop up window and close the pipeline tab. You do not need to select a folder yet.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>