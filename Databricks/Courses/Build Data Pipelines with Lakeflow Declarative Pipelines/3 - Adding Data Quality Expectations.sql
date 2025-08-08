-- Databricks notebook source
-- MAGIC %md
-- MAGIC
-- MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
-- MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
-- MAGIC </div>
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC # 3 - Adding Data Quality Expectations
-- MAGIC
-- MAGIC In this demonstration we will add data quality expectations to apply quality constraints that validates data as it flows through Lakeflow Declarative Pipelines. Expectations provide greater insight into data quality metrics and allow you to fail updates or drop records when detecting invalid records.
-- MAGIC
-- MAGIC
-- MAGIC ### Learning Objectives
-- MAGIC
-- MAGIC By the end of this lesson, you will be able to:
-- MAGIC - Add quality constraints within a Lakeflow Declarative Pipeline to trigger appropriate actions (warn, drop, or fail) based on data expectations.
-- MAGIC - Analyze pipeline metrics to identify and interpret data quality issues across different data flows.

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
-- MAGIC This cell will also reset your `/Volumes/dbacademy/ops/labuser/` volume with the JSON files to the starting point, with one JSON file in each volume.
-- MAGIC
-- MAGIC **NOTE:** The `DA` object is only used in Databricks Academy courses and is not available outside of these courses. It will dynamically create and reference the information needed to run the course.

-- COMMAND ----------

-- MAGIC %run ./Includes/Classroom-Setup-3

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Run the cell below to programmatically view the files in your `/Volumes/dbacademy/ops/labuser/orders` volume. Confirm you only see the original **00.json** file in the **orders** folder.

-- COMMAND ----------

-- DBTITLE 1,View files in the orders volume
-- MAGIC %python
-- MAGIC spark.sql(f'LIST "{DA.paths.working_dir}/orders"').display()

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## B. Adding Data Quality Expectations
-- MAGIC
-- MAGIC This demonstration includes a simple starter Lakeflow Declarative Pipeline that has already been created. We will continue to build on it to explore it's capabilities.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Run the cell below to create your starter pipeline for this demonstration. The pipeline will set the following for you:
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

-- DBTITLE 1,Create pipeline 3
-- MAGIC %python
-- MAGIC create_declarative_pipeline(pipeline_name=f'3 - Adding Data Quality Expectations Project - {DA.catalog_name}', 
-- MAGIC                             root_path_folder_name='3 - Adding Data Quality Expectations Project',
-- MAGIC                             catalog_name = DA.catalog_name,
-- MAGIC                             schema_name = 'default',
-- MAGIC                             source_folder_names=['orders'],
-- MAGIC                             configuration = {'source':DA.paths.working_dir})

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Complete the following steps to open the starter pipeline for this demonstration:
-- MAGIC
-- MAGIC    a. Click the folder icon ![Folder](./Includes/images/folder_icon.png) in the left navigation panel.
-- MAGIC    
-- MAGIC    b. In the **Build Data Pipelines with Lakeflow Declarative Pipelines** folder, find the **3 - Adding Data Quality Expectations Project** folder.
-- MAGIC    
-- MAGIC    c. Right-click and select **Open in a new tab**.
-- MAGIC
-- MAGIC    d. In the new tab:
-- MAGIC       - Select the **orders** folder (The main folder also contains the extra **python_excluded** folder that contains the Python version)
-- MAGIC
-- MAGIC       - Click on **orders_pipeline.sql**.
-- MAGIC       
-- MAGIC
-- MAGIC    e. In the navigation pane of the new tab, you should see **Pipeline** and **All Files**. Ensure you are in the **Pipeline** tab. This will list all files in your pipeline.
-- MAGIC    <br></br>
-- MAGIC    **Example**
-- MAGIC    
-- MAGIC    ![Pipeline and All Files Tab](./Includes/images/pipeline_projecttabs.png)
-- MAGIC
-- MAGIC #### IMPORTANT
-- MAGIC    **NOTE:** If you open the **orders_pipeline.sql** file and it does not open up the pipeline editor, that is because that folder is not associated with a pipeline. Please make sure to run the previous cell to associate the folder with the pipeline and try again.
-- MAGIC
-- MAGIC    **WARNING:** If you get the following warning when opening the **orders_pipeline.sql** file: 
-- MAGIC
-- MAGIC    ```pipeline you are trying to access does not exist or is inaccessible. Please verify the pipeline ID, request access or detach this file from the pipeline.``` 
-- MAGIC
-- MAGIC    Simply refresh the page and/or reselect the notebook.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. In the new tab, follow the instructions provided in the comments within the **orders_pipeline.sql** file.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Additional Resources
-- MAGIC
-- MAGIC - [Manage data quality with pipeline expectations](https://docs.databricks.com/aws/en/dlt/expectations)
-- MAGIC
-- MAGIC - [Expectation recommendations and advanced patterns](https://docs.databricks.com/aws/en/dlt/expectation-patterns)
-- MAGIC
-- MAGIC - [Data Quality Management With Databricks](https://www.databricks.com/discover/pages/data-quality-management#expectations-with-delta-live-tables)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC
-- MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
-- MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
-- MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
-- MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>