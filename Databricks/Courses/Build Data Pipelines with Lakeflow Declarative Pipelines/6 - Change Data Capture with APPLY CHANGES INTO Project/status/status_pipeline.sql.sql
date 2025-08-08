-- Databricks notebook source
-- MAGIC %md
-- MAGIC
-- MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
-- MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
-- MAGIC </div>
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC # Status Pipeline
-- MAGIC
-- MAGIC In this DLT pipeline, the **status** pipeline is implemented within a notebook. DLT supports using `.py`, `.sql`, or notebook files as pipeline sources.
-- MAGIC
-- MAGIC **NOTE:** In an notebook you must use either Python or SQL. 
-- MAGIC
-- MAGIC The final pipeline performs the following tasks:
-- MAGIC
-- MAGIC 1. Creates the **status_bronze_demo5** streaming table by ingesting raw JSON files from `/Volumes/dbacademy/ops/your-lab-user/status/`.
-- MAGIC
-- MAGIC 2. Creates the **status_silver_demo5** streaming table from the **status_bronze_demo5** table.
-- MAGIC
-- MAGIC 3. Creates the materialized view **full_order_status_gold_demo5** to capture each order's status by joining the following tables:
-- MAGIC    - **status_silver_demo5**
-- MAGIC    - **orders_silver_demo5**
-- MAGIC
-- MAGIC 4. Creates the following materialized views:
-- MAGIC    - **cancelled_orders_gold_demo5** – Displays all cancelled orders and how many days passed before cancellation.
-- MAGIC    - **delivered_orders_gold_demo5** – Displays all delivered orders and how many days it took to deliver each order.
-- MAGIC ![Pipeline](../../Includes/images/demo6_pipeline_image.png)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## A. JSON -> Bronze
-- MAGIC The code below ingests JSON files located in your `/Volumes/dbacademy/ops/your-lab-user/status/` volume, using the `source` DLT configuration parameter to point to the base path `/Volumes/dbacademy/ops/your-lab-user/`.

-- COMMAND ----------

CREATE OR REFRESH STREAMING TABLE 1_bronze_db.status_bronze_demo6
  COMMENT "Ingest raw JSON order status files from cloud storage"
  TBLPROPERTIES (
    "quality" = "bronze",
    "pipelines.reset.allowed" = false     -- prevent full table refreshes on the bronze table
  )
AS 
SELECT 
  *,
  current_timestamp() processing_time, 
  _metadata.file_name AS source_file
FROM STREAM read_files(
  "${source}/status", 
  format => "json");

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## B. Bronze -> Silver
-- MAGIC The code below performs a simple transformation on the date field and selects only the necessary columns for the silver streaming table **status_silver_demo5**.  
-- MAGIC
-- MAGIC We're also adding a comment and table properties to document the table for production use, along with DLT expectations to enforce data quality on the streaming table.

-- COMMAND ----------

CREATE OR REFRESH STREAMING TABLE 2_silver_db.status_silver_demo6
  (
    -- Drop rows if order_status_timestamp is not valid
    CONSTRAINT valid_timestamp EXPECT (order_status_timestamp > "2021-12-25") ON VIOLATION DROP ROW,
    -- Warn if order_status is not in the following
    CONSTRAINT valid_order_status EXPECT (order_status IN ('on the way','canceled','return canceled','delivered','return processed','placed','preparing'))
  )
  COMMENT "Order with each status and timestamp"
  TBLPROPERTIES ("quality" = "silver")
AS 
SELECT
  order_id,
  order_status,
  timestamp(status_timestamp) AS order_status_timestamp
FROM STREAM 1_bronze_db.status_bronze_demo6;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## C. Use a Materialized View to Join Two Tables
-- MAGIC One way to join two streaming tables in DLT is by creating a materialized view that performs the join.  This approach takes all rows from each streaming table and executes a full inner join operation.
-- MAGIC
-- MAGIC **NOTES:**
-- MAGIC
-- MAGIC - **Materialized views include built-in optimizations where applicable:**
-- MAGIC   - [Incremental refresh for materialized views](https://docs.databricks.com/aws/en/optimizations/incremental-refresh)
-- MAGIC   - [Delta Live Tables Announces New Capabilities and Performance Optimizations](https://www.databricks.com/blog/2022/06/29/delta-live-tables-announces-new-capabilities-and-performance-optimizations.html)
-- MAGIC   - [Cost-effective, incremental ETL with serverless compute for Delta Live Tables pipelines](https://www.databricks.com/blog/cost-effective-incremental-etl-serverless-compute-delta-live-tables-pipelines)
-- MAGIC
-- MAGIC - **Stateful joins (Stream to Stream):** For stateful joins in DLT (i.e., joining incrementally as data is ingested), refer to the [Optimize stateful processing in DLT with watermarks](https://docs.databricks.com/aws/en/dlt/stateful-processing) documentation. **Stateful joins are an advanced topic and outside the scope of this course.**

-- COMMAND ----------

CREATE OR REFRESH MATERIALIZED VIEW 3_gold_db.full_order_info_gold_demo6
  COMMENT "Joining the orders and order status silver tables to view all orders with each individual status per order"
  TBLPROPERTIES ("quality" = "gold")
AS 
SELECT
  orders.order_id,
  orders.order_timestamp,
  status.order_status,
  status.order_status_timestamp
-- Notice that the STREAM keyword was not used when referencing the streaming tables
FROM 2_silver_db.status_silver_demo6 status    
  INNER JOIN 2_silver_db.orders_silver_demo6 orders 
  ON orders.order_id = status.order_id;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## D. Create Materialized Views for Cancelled and Delivered Orders

-- COMMAND ----------

-- MAGIC %md
-- MAGIC The code below will create two tables using the joined data from above:
-- MAGIC
-- MAGIC - **3_gold_db.cancelled_orders_gold_demo5**
-- MAGIC     - A materialized view containing all **cancelled** orders
-- MAGIC     - number of days it took to cancel each order.
-- MAGIC
-- MAGIC - **3_gold_db.delivered_orders_gold_demo5**
-- MAGIC     - A materialized view containing all **delivered** orders
-- MAGIC     - number of days it took to deliver each order.
-- MAGIC
-- MAGIC     [datediff function](https://docs.databricks.com/aws/en/sql/language-manual/functions/datediff)

-- COMMAND ----------

-- CANCELLED ORDERS MV
CREATE OR REFRESH MATERIALIZED VIEW 3_gold_db.cancelled_orders_gold_demo6
  COMMENT "All cancelled orders"
  TBLPROPERTIES ("quality" = "gold")
AS 
SELECT
  order_id,
  order_timestamp,
  order_status,
  order_status_timestamp,
  datediff(DAY,order_timestamp, order_status_timestamp) AS days_to_cancel -- calculate days to cancel
FROM 3_gold_db.full_order_info_gold_demo6
WHERE order_status = 'canceled';




-- DELIVERED ORDERS MV
CREATE OR REFRESH MATERIALIZED VIEW 3_gold_db.delivered_orders_gold_demo6
  COMMENT "All delivered orders"
  TBLPROPERTIES ("quality" = "gold")
AS 
SELECT
  order_id,
  order_timestamp,
  order_status,
  order_status_timestamp,
  datediff(DAY,order_timestamp, order_status_timestamp) AS days_to_delivery -- calculate days to deliver
FROM 3_gold_db.full_order_info_gold_demo6
WHERE order_status = 'delivered';

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## E. Create the Production Pipeline
-- MAGIC Follow the steps below to modify the pipeline settings and run the production pipeline.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Complete the following steps to modify your pipeline configuration for production:
-- MAGIC
-- MAGIC    a. Select the **Settings** icon ![Pipeline Settings](../../Includes/images/pipeline_settings_icon.png) in the left navigation pane.
-- MAGIC
-- MAGIC    b. In the **Pipeline settings** section, you can modify the **Pipeline name** and **Run as** settings.
-- MAGIC
-- MAGIC       - Click the pencil icon ![pencil_settings_icon.png](../../Includes/images/pencil_settings_icon.png) next to **Run as**.
-- MAGIC
-- MAGIC       - You can optionally change the executor of the pipeline to a service principal.  
-- MAGIC         A service principal is an identity you create in Databricks for use with automated tools, jobs, and applications.  
-- MAGIC
-- MAGIC         - For more information, see the [What is a service principal?](https://docs.databricks.com/aws/en/admin/users-groups/service-principals#what-is-a-service-principal) documentation.
-- MAGIC
-- MAGIC       - For this course select **Cancel** and leave **Run as** set to your username.
-- MAGIC
-- MAGIC    c. In the **Code assets** section, confirm that:
-- MAGIC
-- MAGIC       - **Root folder** points to this DLT project (**5 - Deploying a DLT Pipeline to Production**).
-- MAGIC
-- MAGIC       - **Source code** references the **orders** and **status** folders within this project.
-- MAGIC
-- MAGIC    d. In the **Default location for data assets** section, confirm the following:
-- MAGIC
-- MAGIC       - **Default catalog** is your **labuser** catalog.
-- MAGIC
-- MAGIC       - **Default schema** is the **default** schema.
-- MAGIC
-- MAGIC    e. In the **Compute** section, confirm that **Serverless** compute is selected.
-- MAGIC
-- MAGIC    f. In the **Configuration** section, ensure that the `source` key is set to your data source volume path:  
-- MAGIC       `/Volumes/dbacademy/ops/your-labuser-name`
-- MAGIC
-- MAGIC    g. In the **Tags** section you can add takes to help determine usage per department/chargeback.. We will leave them as is. 
-- MAGIC
-- MAGIC    h. In the **Advanced settings** section:
-- MAGIC    
-- MAGIC       - Expand **Advanced settings**.
-- MAGIC
-- MAGIC       - Click **Edit advanced settings**.
-- MAGIC
-- MAGIC       - In **Pipeline mode**, ensure **Triggered** is selected so the pipeline runs on a schedule.  
-- MAGIC         - Alternatively, you can choose **Continuous** mode to keep the pipeline running at all times.  
-- MAGIC         - For more details, see [Triggered vs. continuous pipeline mode](https://docs.databricks.com/aws/en/dlt/pipeline-mode).
-- MAGIC
-- MAGIC       - In **PIpeline user mode** select **Production**.
-- MAGIC
-- MAGIC       - For **Channel**, you can leave it as **Preview** for training purposes:
-- MAGIC         - **Current** – Uses the latest stable Databricks Runtime version, recommended for production.
-- MAGIC         - **Preview** – Uses a more recent, potentially less stable Runtime version, ideal for testing upcoming features.
-- MAGIC         - View the [DLT release notes and the release upgrade process](https://docs.databricks.com/aws/en/release-notes/dlt/) documentation for more information.
-- MAGIC
-- MAGIC       - In the **Event logs** section:
-- MAGIC         - Select **Publish event log to metastore**.
-- MAGIC         - Set **Event log name** to `event_log_demo_5`.
-- MAGIC         - Set **Event log catalog** to your **labuser** catalog.
-- MAGIC         - Set **Event log schema** to the **default** schema.
-- MAGIC
-- MAGIC         **NOTE:** If the event log is not saved to the correct location, the event log exploration steps will not work properly in the main notebook.
-- MAGIC
-- MAGIC    i. Click **Save** to save your DLT pipeline settings.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Once your pipeline is production-ready, you'll want to schedule it to run either on a time interval or continuously.
-- MAGIC
-- MAGIC    For this demonstration, we’ll:
-- MAGIC    - Schedule the pipeline to run every day at 8:00 PM.
-- MAGIC    - Optionally configure notifications to alert you upon job **Start**, **Success**, and **Failure**.  
-- MAGIC      *(If you don’t want email notifications, you can skip this step.)*
-- MAGIC
-- MAGIC    Complete the following steps to schedule the pipeline:
-- MAGIC
-- MAGIC    a. Select the **Schedule** button.
-- MAGIC
-- MAGIC    b. For the job name, leave it as **5 - Deploying a DLT Pipeline to Production Project - labuser-name**.
-- MAGIC
-- MAGIC    c. Below **Job name**, select **Advanced**.
-- MAGIC
-- MAGIC    d. In the **Schedule** section, configure the following:
-- MAGIC    - Set the **Day**.
-- MAGIC    - Set the time to **20:00** (8:00 PM).
-- MAGIC    - Leave the **Timezone** as default.
-- MAGIC    - Select **More options**, and under **Notifications**, add your email to receive alerts for:
-- MAGIC      - **Start**
-- MAGIC      - **Success**
-- MAGIC      - **Failure**
-- MAGIC
-- MAGIC    e. Click **Create** to save and schedule the job.
-- MAGIC
-- MAGIC   **NOTE:** You could also set the pipeline to run a few minutes after your current time to see it start through the scheduler.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. After completing the pipeline settings and scheduling the pipeline, let's manually trigger the pipeline by selecting the **Run pipeline** button.
-- MAGIC
-- MAGIC     While the pipeline is running, you can explore what the final pipeline will look like using the image below:
-- MAGIC
-- MAGIC     ![DLT Pipeline Demo 6](../../Includes/images/demo6_pipeline_image.png) 
-- MAGIC
-- MAGIC **NOTE:** Currently we have one JSON file in both **status** and **orders**.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 4. After the pipeline has completed it's first run, complete the following:
-- MAGIC
-- MAGIC    a. Examine the **Pipeline graph** and confirm:
-- MAGIC       - 174 rows were read into the **orders_bronze** and **orders_silver** streaming tables
-- MAGIC       - 536 rows were read into the **status_bronze** and **status_silver** streaming tables
-- MAGIC       - 536 rows are in the **full_order_info_gold** materialized view
-- MAGIC       - 7 rows are in the **orders_by_date_gold** materialized view
-- MAGIC       - 8 rows are in the **cancelled_orders_gold** materialized view
-- MAGIC       - 94 rows are in the **delivered_orders_gold** materialized view
-- MAGIC
-- MAGIC    b. Go back to the main notebook **5 - Deploying a DLT Pipeline to Production**
-- MAGIC    
-- MAGIC    c. Complete the steps in step **D. Land Data Data to Your Data Source Volume**.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 5. After you have landed **4** new files into the data source volume, run the pipeline to process the newly landed JSON files.
-- MAGIC
-- MAGIC    Notice the following:
-- MAGIC
-- MAGIC    a. The **status** bronze to silver flow ingests 410 new rows.
-- MAGIC
-- MAGIC    b. The **orders** bronze to silver flow ingests 98 new rows.
-- MAGIC
-- MAGIC    c. The **full_order_info_gold** materialized view join contains a total of 946 rows (the previous 536 rows + the new 410 rows).
-- MAGIC
-- MAGIC    d. The **cancelled_orders_gold** materialized view contains 21 rows.
-- MAGIC
-- MAGIC    e. The **delivered_orders_gold** materialized view contains 176 rows.
-- MAGIC
-- MAGIC    f. The **orders_by_date_gold** materialized view contains 11 rows.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 6. In the window at the bottom, select the **Expectations** link for the **status_silver_demo5** table. It should contain the value **2**. Notice that in this run, 7.6% (31 rows) for the **valid_order_status** expectation returned a warning.
-- MAGIC
-- MAGIC This is something we would want to investigate and address in future stages of the pipeline.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 7. Go back to the main notebook **5 - Deploying a DLT Pipeline to Production** and complete the steps in step **E. Monitor Your Pipeline with the Event Log**.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC
-- MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
-- MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
-- MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
-- MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>