-- Databricks notebook source
-- MAGIC %md
-- MAGIC
-- MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
-- MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
-- MAGIC </div>
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC # 5 - Deploying a Pipeline to Production
-- MAGIC
-- MAGIC In this demonstration, we will begin by adding an additional data source to our pipeline and performing a join with our streaming tables. Then, we will focus on productionalizing the pipeline by adding comments and table properties to the objects we create, scheduling the pipeline, and creating an event log to monitor the pipeline.
-- MAGIC
-- MAGIC ### Learning Objectives
-- MAGIC
-- MAGIC By the end of this lesson, you will be able to:
-- MAGIC - Apply the appropriate comment syntax and table properties to pipeline objects to enhance readability.
-- MAGIC - Demonstrate how to perform a join between two streaming tables using a materialized view to optimize data processing.
-- MAGIC - Execute the scheduling of a pipeline using trigger or continuous modes to ensure timely processing.
-- MAGIC - Explore the event log to monitor a production Lakeflow Declarative Pipeline.

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

-- MAGIC %run ./Includes/Classroom-Setup-5

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## B. Explore the Orders and Status JSON Files

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Explore the raw data located in the `/Volumes/dbacademy/ops/our-lab-user/orders/` volume. This is the data we have been working with throughout the course demonstrations.
-- MAGIC
-- MAGIC    Run the cell below to view the results. Notice that the orders JSON file(s) contains information about when each order was placed.

-- COMMAND ----------

-- DBTITLE 1,Preview the orders data source files
SELECT *
FROM read_files(
  DA.paths_working_dir || '/orders/',
  format => 'JSON'
)
LIMIT 10;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Explore the **status** raw data located in the `/Volumes/dbacademy/ops/your-lab-user/status/` volume and filter for the specific **order_id** *75123*.
-- MAGIC
-- MAGIC    Run the cell below to view the results. Notice that the status JSON file(s) contain **order_status** information for each order.  
-- MAGIC    
-- MAGIC    **NOTE:** The **order_status** can include multiple rows per order and may be any of the following:
-- MAGIC    
-- MAGIC    - on the way  
-- MAGIC    - canceled  
-- MAGIC    - return canceled  
-- MAGIC    - reported shipping error  
-- MAGIC    - delivered  
-- MAGIC    - return processed  
-- MAGIC    - return picked up  
-- MAGIC    - placed  
-- MAGIC    - preparing  
-- MAGIC    - return requested
-- MAGIC

-- COMMAND ----------

-- DBTITLE 1,Preview the status data source files
SELECT *
FROM read_files(
  DA.paths_working_dir || '/status/',
  format => 'JSON'
)
WHERE order_id = 75123;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. One of our objectives is to join the **orders** data with the order **status** data.  
-- MAGIC
-- MAGIC     The query below demonstrates what the result of the final join in the Lakeflow Declarative Pipeline will look like after the data has been incrementally ingested and cleaned when we create the pipeline. Run the cell and review the output.
-- MAGIC
-- MAGIC     Notice that after joining the tables, we can see each **order_id** along with its original **order_timestamp** and the **order_status** at specific points in time.
-- MAGIC
-- MAGIC **NOTE:** The data used in this demo is artificially generated, so the **order_status_timestamps** may not reflect realistic timing.

-- COMMAND ----------

-- DBTITLE 1,Perform a join to preview the desired result
WITH orders AS (
  SELECT *
  FROM read_files(
        DA.paths_working_dir || '/orders/',
        format => 'JSON'
  )
),
status AS (
  SELECT *
  FROM read_files(
        DA.paths_working_dir || '/status/',
        format => 'JSON'
  )
)
-- Join the views to get the order history with status
SELECT
  orders.order_id,
  timestamp(orders.order_timestamp) AS order_timestamp,
  status.order_status,
  timestamp(status.status_timestamp) AS order_status_timestamp
FROM orders
  INNER JOIN status 
  ON orders.order_id = status.order_id
ORDER BY order_id, order_status_timestamp;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## C. Putting a Pipeline in Production
-- MAGIC
-- MAGIC This course includes a complete Lakeflow Declarative Pipeline project that has already been created.  In this section, you'll explore the Lakeflow Declarative Pipeline modify its settings for production use.
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. The screenshot below shows what the final Lakeflow Declarative Pipeline will look like when ingesting a single JSON file from the data sources:  
-- MAGIC ![Final Demo 6 Pipeline](./Includes/images/demo6_pipeline_image.png)
-- MAGIC
-- MAGIC     **Note:** Depending on the number of files you've ingested, the row count may vary.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Run the cell below to create your starter Lakeflow Declarative Pipeline for this demonstration. The pipeline will set the following for you:
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

-- DBTITLE 1,Create pipeline 5
-- MAGIC %python
-- MAGIC create_declarative_pipeline(pipeline_name=f'5 - Deploying a Pipeline to Production Project - {DA.catalog_name}', 
-- MAGIC                             root_path_folder_name='5 - Deploying a Pipeline to Production Project',
-- MAGIC                             catalog_name = DA.catalog_name,
-- MAGIC                             schema_name = 'default',
-- MAGIC                             source_folder_names=['orders', 'status'],
-- MAGIC                             configuration = {'source':DA.paths.working_dir})

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. Complete the following steps to open the starter Lakeflow Declarative Pipeline project for this demonstration:
-- MAGIC
-- MAGIC    a. Click the folder icon ![Folder](./Includes/images/folder_icon.png) in the left navigation panel.
-- MAGIC
-- MAGIC    b. In the **Build Data Pipelines with Lakeflow Declarative Pipelines** folder, find the **5 - Deploying a Pipeline to Production Project** folder. 
-- MAGIC    
-- MAGIC    c. Right-click and select **Open in a new tab**.
-- MAGIC
-- MAGIC    d. In the new tab you should see three folders: **explorations**, **orders**, and **status** (plus the extra **python_excluded** folder that contains the Python version). 
-- MAGIC
-- MAGIC    e. Continue to step 4 and 5 below.
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
-- MAGIC ##### Explore the code in the `orders/orders_pipeline.sql` file
-- MAGIC
-- MAGIC 4. In the new tab select the **orders** folder. It contains the same **orders_pipeline.sql** pipeline you've been working with.  Follow the instructional comments in the file to proceed.
-- MAGIC
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ##### Explore the code in the `status/status_pipeline` notebook
-- MAGIC
-- MAGIC 5. After reviewing the **orders_pipeline.sql** file, you'll be directed to explore the **status/status_pipeline.sql** notebook. This notebook processes new data and adds it to the pipeline. Follow the instructions provided in the notebook's markdown cells.
-- MAGIC
-- MAGIC     **NOTE:** The **status/status_pipeline.sql**  notebook will go through setting up the pipeline settings, scheduling and running the production pipeline.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## D. Land More Data to Your Data Source Volume

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Run the cell below to add **4** more JSON files to your **orders** and **status** volume.

-- COMMAND ----------

-- DBTITLE 1,Copy files into the data source volumes
-- MAGIC %python
-- MAGIC copy_files(copy_from = '/Volumes/dbacademy_retail/v01/retail-pipeline/orders/stream_json', 
-- MAGIC            copy_to = f'{DA.paths.working_dir}/orders', 
-- MAGIC            n = 5)
-- MAGIC
-- MAGIC copy_files(copy_from = '/Volumes/dbacademy_retail/v01/retail-pipeline/status/stream_json', 
-- MAGIC            copy_to = f'{DA.paths.working_dir}/status', 
-- MAGIC            n = 5)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Complete the follow to confirm new JSON files were added to your volume:
-- MAGIC
-- MAGIC    a. Select the **Catalog** icon ![Catalog Icon](./Includes/images/catalog_icon.png) in the left navigation bar.
-- MAGIC
-- MAGIC    b. Expand the **dbacademy** catalog.
-- MAGIC
-- MAGIC    c. Expand the **ops** schema.
-- MAGIC
-- MAGIC    d. Expand your **labuser** volume. You should notice that your volume contains three folders:
-- MAGIC    - **customers**
-- MAGIC    - **orders**
-- MAGIC    - **status**
-- MAGIC
-- MAGIC    e. Expand the **orders** and **status** folders.
-- MAGIC
-- MAGIC    f. Notice that we have landed new data in our data source for the pipeline. You should have a total of **5** JSON files in each.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. Navigate back to your pipeline and select **Run pipeline** to process the new landed files.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## E. Introduction to the Pipeline Event Log (Advanced Topic)
-- MAGIC
-- MAGIC After running your pipeline and successfully publishing the event log as a table named **event_log_demo_5** in your **labuser.default** schema (database), begin exploring the event log. 
-- MAGIC
-- MAGIC Here we will quickly introduce the event log. **To process the event log you will need knowledge of parsing JSON formatted strings.**
-- MAGIC
-- MAGIC   - [Monitor Lakeflow Declarative Pipelines](https://docs.databricks.com/aws/en/dlt/observability) documentation
-- MAGIC
-- MAGIC **TROUBLESHOOT:** 
-- MAGIC - **REQUIRED:** If you did not run the pipeline and publish the event log, the code below will not run. Please make sure to complete all steps before starting this section.
-- MAGIC
-- MAGIC - **HIDDEN EVENT LOG:** By default, Lakeflow Declarative Pipelines writes the event log to a hidden Delta table in the default catalog and schema configured for the pipeline. While hidden, the table can still be queried by all sufficiently privileged users. By default, only the owner of the pipeline can query the event log table. By default, the name for the hidden event log is formatted as:  
-- MAGIC   - `catalog.schema.event_log_{pipeline_id}` – where the pipeline ID is the system-assigned UUID with dashes replaced by underscores.  
-- MAGIC   - [Query the Event Log](https://docs.databricks.com/aws/en/dlt/observability#query-the-event-log)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Complete the following steps to view the **labuser.default.event_log_demo_5** event log in your catalog:
-- MAGIC
-- MAGIC    a. Select the catalog icon ![Catalog Icon](./Includes/images/catalog_icon.png) from the left navigation pane.
-- MAGIC
-- MAGIC    b. Expand your **labuser** catalog.
-- MAGIC
-- MAGIC    c. Expand the following schemas (databases):
-- MAGIC       - **1_bronze_db**
-- MAGIC       - **2_silver_db**
-- MAGIC       - **3_gold_db**
-- MAGIC       - **default**
-- MAGIC
-- MAGIC    d. Notice the following:
-- MAGIC       - In the **1_bronze_db**, **2_silver_db**, and **3_gold_db** schemas, the pipeline streaming tables and materialized views were created (they end with **demo5**).
-- MAGIC       - In the **default** schema, the pipeline has published the event log as a table named **event_log_demo_5**.
-- MAGIC
-- MAGIC **NOTE:** You might need to refresh the catalogs to view the streaming tables, materialized views, and event log.
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Query your **labuser.default.event_log_demo_5** table to see what the event log looks like.
-- MAGIC
-- MAGIC    Notice that it contains all events within the pipeline as **STRING** columns (typically JSON-formatted strings) or **STRUCT** columns. Databricks supports the `:` (colon) operator to parse JSON fields. See the [`:` operator documentation](https://docs.databricks.com/) for more details.
-- MAGIC
-- MAGIC    The following table describes the event log schema. Some fields contain JSON data—such as the **details** field—which must be parsed to perform certain queries.

-- COMMAND ----------

-- DBTITLE 1,View the event log
SELECT *
FROM default.event_log_demo_5;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC | Field          | Description |
-- MAGIC |----------------|-------------|
-- MAGIC | `id`           | A unique identifier for the event log record. |
-- MAGIC | `sequence`     | A JSON document containing metadata to identify and order events. |
-- MAGIC | `origin`       | A JSON document containing metadata for the origin of the event, for example, the cloud provider, the cloud provider region, user_id, pipeline_id, or pipeline_type to show where the pipeline was created, either DBSQL or WORKSPACE. |
-- MAGIC | `timestamp`    | The time the event was recorded. |
-- MAGIC | `message`      | A human-readable message describing the event. |
-- MAGIC | `level`        | The event type, for example, INFO, WARN, ERROR, or METRICS. |
-- MAGIC | `maturity_level` | The stability of the event schema. The possible values are:<br><br>- **STABLE**: The schema is stable and will not change.<br>- **NULL**: The schema is stable and will not change. The value may be NULL if the record was created before the maturity_level field was added (release 2022.37).<br>- **EVOLVING**: The schema is not stable and may change.<br>- **DEPRECATED**: The schema is deprecated and the pipeline runtime may stop producing this event at any time. |
-- MAGIC | `error`        | If an error occurred, details describing the error. |
-- MAGIC | `details`      | A JSON document containing structured details of the event. This is the primary field used for analyzing events. |
-- MAGIC | `event_type`   | The event type. |
-- MAGIC
-- MAGIC **[Event Log Schema](https://docs.databricks.com/aws/en/dlt/observability#event-log-schema)**

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. The majority of the detailed information you will want from the event log is located in the **details** column, which is a JSON-formatted string. You will need to parse this column.
-- MAGIC
-- MAGIC    You can find more information in the Databricks documentation on how to [query JSON strings](https://docs.databricks.com/aws/en/semi-structured/json).
-- MAGIC
-- MAGIC    The code below will:
-- MAGIC
-- MAGIC    - Return the **event_type** column.
-- MAGIC
-- MAGIC    - Return the entire **details** JSON-formatted string.
-- MAGIC
-- MAGIC    - Parse out the **flow_progress** values from the **details** JSON-formatted string, if they exist.
-- MAGIC    
-- MAGIC    - Parse out the **user_action** values from the **details** JSON-formatted string, if they exist.
-- MAGIC

-- COMMAND ----------

SELECT
  id,
  event_type,
  details,
  details:flow_progress,
  details:user_action
FROM default.event_log_demo_5

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 4. One use case for the event log is to examine data quality metrics for all runs of your pipeline. These metrics provide valuable insights into your pipeline, both in the short term and long term. Metrics are captured for each constraint throughout the entire lifetime of the table.
-- MAGIC
-- MAGIC    Below is an example query to obtain those metrics. We won’t dive into the JSON parsing code here. This example simply demonstrates what’s possible with the **event_log**.
-- MAGIC
-- MAGIC    Run the cell and observe the results. Notice the following:
-- MAGIC    - The **passing_records** for each constraint are displayed.
-- MAGIC    - The **failing_records** (WARN) for each constraint are displayed.
-- MAGIC
-- MAGIC **NOTE:** If you have selected **Run pipeline with full table refresh** at any time during your pipeline, your results will include metrics from previous runs as well as from the full refresh. Additional logic is required to isolate results after the full table refresh. This is outside the scope of this course.
-- MAGIC

-- COMMAND ----------

CREATE OR REPLACE TEMPORARY VIEW dq_source_vw AS
SELECT explode(
            from_json(details:flow_progress:data_quality:expectations,
                      "array<struct<name: string, dataset: string, passed_records: int, failed_records: int>>")
          ) AS row_expectations
   FROM default.event_log_demo_5
   WHERE event_type = 'flow_progress';


-- View the data
SELECT 
  row_expectations.dataset as dataset,
  row_expectations.name as expectation,
  SUM(row_expectations.passed_records) as passing_records,
  SUM(row_expectations.failed_records) as warnings_records
FROM dq_source_vw
GROUP BY row_expectations.dataset, row_expectations.name
ORDER BY dataset;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Summary
-- MAGIC
-- MAGIC This was a quick introduction to the pipeline **event_log**. With the **event_log**, you can investigate all aspects of your pipeline runs to explore the runs as well as create overall reports. Feel free to investigate the **event_log** further on your own.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Additional Resources
-- MAGIC
-- MAGIC - [Lakeflow Declarative Pipelines properties reference](https://docs.databricks.com/aws/en/dlt/properties#dlt-table-properties)
-- MAGIC
-- MAGIC - [Table properties and table options](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-tblproperties)
-- MAGIC
-- MAGIC - [Triggered vs. continuous pipeline mode](https://docs.databricks.com/aws/en/dlt/pipeline-mode)
-- MAGIC
-- MAGIC - [Development and production modes](https://docs.databricks.com/aws/en/dlt/updates#development-and-production-modes)
-- MAGIC
-- MAGIC - [Monitor Lakeflow Declarative Pipelines](https://docs.databricks.com/aws/en/dlt/observability)
-- MAGIC
-- MAGIC - **Materialized views include built-in optimizations where applicable:**
-- MAGIC   - [Incremental refresh for materialized views](https://docs.databricks.com/aws/en/optimizations/incremental-refresh)
-- MAGIC   - [Delta Live Tables Announces New Capabilities and Performance Optimizations](https://www.databricks.com/blog/2022/06/29/delta-live-tables-announces-new-capabilities-and-performance-optimizations.html)
-- MAGIC   - [Cost-effective, incremental ETL with serverless compute for Delta Live Tables pipelines](https://www.databricks.com/blog/cost-effective-incremental-etl-serverless-compute-delta-live-tables-pipelines)
-- MAGIC
-- MAGIC - **Stateful joins:** For stateful joins in pipelines (i.e., joining incrementally as data is ingested), refer to the [Optimize stateful processing in Lakeflow Declarative Pipelines with watermarks](https://docs.databricks.com/aws/en/dlt/stateful-processing) documentation. **Stateful joins are an advanced topic and outside the scope of this course.**

-- COMMAND ----------

-- MAGIC %md
-- MAGIC
-- MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
-- MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
-- MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
-- MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>