# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # 3 - Explore Scheduling Options
# MAGIC
# MAGIC In the last lesson, we manually triggered our job. In this lesson, we will explore three other types of triggers we can use in our Databricks Workflow Jobs:
# MAGIC 1. Scheduled
# MAGIC 1. File arrival
# MAGIC 1. Continuous

# COMMAND ----------

# MAGIC %md
# MAGIC ## REQUIRED - SELECT CLASSIC COMPUTE
# MAGIC
# MAGIC Before executing cells in this notebook, please select your classic compute cluster in the lab. Be aware that **Serverless** is enabled by default.
# MAGIC
# MAGIC Follow these steps to select the classic compute cluster:
# MAGIC
# MAGIC
# MAGIC 1. Navigate to the top-right of this notebook and click the drop-down menu to select your cluster. By default, the notebook will use **Serverless**.
# MAGIC
# MAGIC 2. If your cluster is available, select it and continue to the next cell. If the cluster is not shown:
# MAGIC
# MAGIC    - Click **More** in the drop-down.
# MAGIC
# MAGIC    - In the **Attach to an existing compute resource** window, use the first drop-down to select your unique cluster.
# MAGIC
# MAGIC **NOTE:** If your cluster has terminated, you might need to restart it in order to select it. To do this:
# MAGIC
# MAGIC 1. Right-click on **Compute** in the left navigation pane and select *Open in new tab*.
# MAGIC
# MAGIC 2. Find the triangle icon to the right of your compute cluster name and click it.
# MAGIC
# MAGIC 3. Wait a few minutes for the cluster to start.
# MAGIC
# MAGIC 4. Once the cluster is running, complete the steps above to select your cluster.

# COMMAND ----------

# MAGIC %md
# MAGIC ## A. Classroom Setup
# MAGIC
# MAGIC Run the following cell to configure your working environment for this course. It will also set your default catalog to **dbacademy** and the schema to your specific schema name shown below using the `USE` statements.
# MAGIC <br></br>
# MAGIC ```
# MAGIC USE CATALOG dbacademy;
# MAGIC USE SCHEMA dbacademy.<your unique schema name>;
# MAGIC ```
# MAGIC
# MAGIC **NOTE:** The **DA** object is only used in Databricks Academy courses and is not available outside of these courses.

# COMMAND ----------

# MAGIC %run ./Includes/Classroom-Setup-3

# COMMAND ----------

# MAGIC %md
# MAGIC **NOTE:** If you have already completed the demonstration and want to repeat it, uncomment and run the `DA.delete_baby_names_csv()` method to remove the CSV file used in this demonstration.

# COMMAND ----------

# DA.delete_baby_names_csv()

# COMMAND ----------

# MAGIC %md
# MAGIC ## B. Create a Job
# MAGIC
# MAGIC The following method uses the Databricks SDK to programmatically create a job named **&lt;your-schema&gt;_Lesson03** for the demonstration. The task in the job uses the **Task Notebooks/Lesson 3 Notebooks/View Baby Names** notebook.
# MAGIC
# MAGIC **NOTE:** You can find the method definition that uses the Databricks SDK to create the job in the [Classroom-Setup-3]($./Includes/Classroom-Setup-3) notebook. However, the [Databricks SDK](https://databricks-sdk-py.readthedocs.io/en/latest/) is outside the scope of this course.
# MAGIC
# MAGIC 1. Run the next cell to automatically set up the single-task job named **&lt;your-schema&gt;_Lesson03**. Confirm that the cell output created the job. If the job is already created, an error will be returned.
# MAGIC

# COMMAND ----------

DA.create_job_lesson03()

# COMMAND ----------

# MAGIC %md
# MAGIC 2. View the new job **Labusername_Lesson_03**:
# MAGIC
# MAGIC     a. Right-click on **Jobs and Pipelines** in the left navigation bar and select *Open Link in New Tab*.
# MAGIC
# MAGIC     b. Confirm that you see the job **Labusername_Lesson_03**. Select the job to open it.
# MAGIC
# MAGIC     c. Select **Tasks** in the top navigation bar. The job should contain a single task named **View_New_CSV_Data**.
# MAGIC
# MAGIC     d. View the **Path** of the task. Confirm that the path is using the **Task Notebooks/Lesson 3 Notebooks/View Baby Names** 
# MAGIC    notebook.
# MAGIC     
# MAGIC     e. View the **Compute** of the task. Confirm that it is using **Serverless**.
# MAGIC
# MAGIC     f. Leave the job page open and return to below instructions.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Explore Scheduling Options
# MAGIC Complete the following steps:
# MAGIC 1. Return to your job.
# MAGIC
# MAGIC 2. Make sure you are in the **Tasks** tab of your job.
# MAGIC
# MAGIC 3. On the right hand side of the Jobs UI, locate the **Job Details** section. 
# MAGIC    - **NOTE:** If side panel is collapsed, click the left-hand arrowhead icon to expand it.
# MAGIC
# MAGIC 4. Under the **Schedules & Triggers** section, select the **Add trigger** button to explore the options. There are three options (in addition to manual):
# MAGIC    * **Scheduled** - uses a cron scheduling UI.
# MAGIC       - This UI provides extensive options for setting up chronological scheduling of your Jobs. Settings configured with the UI can also be output in cron syntax, which can be edited if you need custom configuration that is not available with the UI.
# MAGIC
# MAGIC    * **Continuous** - runs over and over with a small amount of time between runs.
# MAGIC
# MAGIC    * **File arrival** - monitors either an external location or a volume for new files. Note the **Advanced** settings, where you can change the time to wait between checks and the time to wait after a new file arrives before starting a run.
# MAGIC
# MAGIC 5. Leave the **Schedules & Triggers** open and return to below instructions.

# COMMAND ----------

# MAGIC %md
# MAGIC ## D. Configure the File Arrival Trigger
# MAGIC
# MAGIC Let's configure a file arrival trigger to monitor a volume for new data files.
# MAGIC
# MAGIC 1. Start by running the cell below to create a volume named **trigger_storage_location**, which we will use as the storage location to monitor. The volume will be created in the **dbacademy** catalog within your unique schema.
# MAGIC
# MAGIC **NOTE:**  Databricks volumes are Unity Catalog objects representing a logical volume of storage in a cloud object storage location. Volumes provide capabilities for accessing, storing, governing, and organizing files. You can use volumes to store and access files in any format, including structured, semi-structured, and unstructured data.
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE VOLUME IF NOT EXISTS trigger_storage_location

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC 2. Complete the steps to view your new volume:
# MAGIC
# MAGIC      a. Select the catalog icon on the left and navigate to your schema in the **dbacademy** catalog. Expand your schema.
# MAGIC
# MAGIC      b. In your schema expand **Volumes**. Confirm that the **trigger_storage_location** volume was created.
# MAGIC
# MAGIC      c. Expand the **trigger_storage_location** volume. Confirm that the volume does not contain any files.

# COMMAND ----------

# MAGIC %md
# MAGIC You can also use the `SHOW VOLUMES` statement to view available volumes in your schema.

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW VOLUMES;

# COMMAND ----------

# MAGIC %md
# MAGIC 3. Run the following cell to get the path to this volume using the custom `DA` object created for this course.
# MAGIC
# MAGIC **NOTE:** You can also select your volume under the catalog, click the three ellipses, and then select *Copy volume path* to get the volume path.

# COMMAND ----------

your_volume_path = (f"/Volumes/{DA.catalog_name}/{DA.schema_name}/trigger_storage_location/")
print(your_volume_path)

# COMMAND ----------

# MAGIC %md
# MAGIC 4. Complete the following to configure the **File Arrival** trigger on your job:
# MAGIC
# MAGIC     - a. Navigate back to the browser tab with your job.
# MAGIC
# MAGIC     - b. In your job, **click Add Trigger** in the Job details pane, and under Trigger type, select File Arrival for the trigger type.
# MAGIC
# MAGIC     - c. Paste the path above into the **Storage location** field
# MAGIC
# MAGIC     - d. Click **Test Trigger** to verify the correct path
# MAGIC
# MAGIC       **NOTE:** You should see **Success**. If not, verify that you have run the cell above and copied all of the cell output into **Storage location**
# MAGIC
# MAGIC     - e. Expand the **Advanced** options. Notice that you can set different trigger options.
# MAGIC
# MAGIC     - f. Click **Save**

# COMMAND ----------

# MAGIC %md
# MAGIC ## E. Set Task Parameters
# MAGIC
# MAGIC The notebook we will use to view our baby names needs to know the name of the catalog and schema we are working with. We can configure this using **Task parameters**. This provides flexibility and the ability to reuse code.
# MAGIC
# MAGIC 1. Run the cell below to view your **catalog** and **schema** names.

# COMMAND ----------

print(f"Catalog name: {DA.catalog_name}")
print(f"Schema name: {DA.schema_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC 2. Complete the following steps to **set the Job task parameters**:
# MAGIC
# MAGIC     a. Go back to your job. In **Task details** pane, under **Parameters**, click **Add**.
# MAGIC
# MAGIC     b. Set the following key-value pairs:
# MAGIC       - **catalog** (key) =  *dbacademy* (value) 
# MAGIC       - **schema** (key) = your schema name from the above cell output (value) 
# MAGIC
# MAGIC     d. Click **Save task**.
# MAGIC
# MAGIC     e. Click to open the [./Task Notebooks/Lesson 3 Notebooks/View Baby Names]($./Task Notebooks/Lesson 3 Notebooks/View Baby Names) notebook. This notebook is used in the **View_New_CSV_Data** task. Notice the following:
# MAGIC       - The **my_catalog** variable is obtaining the value from the **catalog** parameter we set in the task using the following:
# MAGIC          - Stores the values from the text input into the variable **my_catalog**:
# MAGIC             - `my_catalog = dbutils.widgets.get('catalog')`
# MAGIC
# MAGIC       - The **my_schema** variable is obtaining the value from the **schema** parameter we set in the task using the following: 
# MAGIC          - Stores the values from the text input into the variable **my_schema**:
# MAGIC             - `my_schema = dbutils.widgets.get('schema')`
# MAGIC
# MAGIC       - The **my_volume_path** variable uses the parameters we set to point to your **trigger_storage_location** volume using:
# MAGIC          - `f"/Volumes/{my_catalog}/{my_schema}/trigger_storage_location/"`
# MAGIC
# MAGIC    - f. Close the **View Baby Names** notebook
# MAGIC
# MAGIC
# MAGIC **Example**
# MAGIC
# MAGIC ![Lesson03_JobTrigger](./Includes/images/Lesson03_JobTrigger.png)

# COMMAND ----------

# MAGIC %md
# MAGIC 3. As soon as we configured our trigger, Databricks began monitoring the storage location for newly arrived files (by default, it will check every one minute). Let's take a look at the status of our job runs.
# MAGIC
# MAGIC    a. In the upper-left corner, click the **Runs** tab
# MAGIC     - We should see a **Trigger status**. If not, wait about a minute. If you don't see one during that time, double-check the steps above to ensure you configured the **File arrival** trigger correctly.
# MAGIC
# MAGIC    b. Note that the trigger has been evaluated, but it has not found any new files, so the job has not run.
# MAGIC
# MAGIC    c. Run the cell below to add a CSV file to your **trigger_storage_location** volume, and wait about 1-2 minutes. You should see a run triggered automatically.
# MAGIC
# MAGIC    d. After the job completes (about 1-2 minutes), click on the **Start time** to view the run. The notebook simply displays the contents of the CSV file.
# MAGIC
# MAGIC
# MAGIC   **NOTE:** You can manually trigger a run using different parameters by going to the job configuration page (click **Edit task** from the **Run output** page), clicking the down arrow next to **Run now** and selecting **Run now with different parameters**.
# MAGIC
# MAGIC   **NOTE:** There is a limit to the number of triggered job runs.

# COMMAND ----------

import requests

## Sends an HTTP GET request to the provided URL and stores the response
response = requests.get("https://health.data.ny.gov/api/views/jxy9-yhdk/rows.csv")

## Converts the byte data into a string using UTF-8 encoding in the variable csvfile
csvfile = response.content.decode("utf-8")

## Uploads the CSV data stored in the csvfile variable to a a volume in your schema
dbutils.fs.put(f"{your_volume_path}/babynames.csv", csvfile, True)

# COMMAND ----------

# MAGIC %md
# MAGIC ## F. Delete the Job
# MAGIC
# MAGIC 1. Navigate back to all of your jobs.
# MAGIC
# MAGIC 2. Find the job you just created, **&lt;Your-Schema &gt;_Lesson_03**.
# MAGIC
# MAGIC 3. To the right of the job, select the three ellipses and choose **Delete job**.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Additional Resources
# MAGIC [Parameterize jobs](https://docs.databricks.com/aws/en/jobs/parameters) documentation
# MAGIC
# MAGIC [Automating jobs with schedules and triggers](https://docs.databricks.com/aws/en/jobs/triggers) documentation

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>