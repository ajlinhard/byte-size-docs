# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # 2 Lab - Create a Job with Multiple Tasks
# MAGIC ### Duration: ~15 minutes
# MAGIC
# MAGIC
# MAGIC In this lab, you'll be configuring a multi-task job comprising of three notebooks.
# MAGIC
# MAGIC ## Learning Objectives
# MAGIC By the end of this lab, you should be able to:
# MAGIC * Schedule a notebook as a task in a Databricks Job
# MAGIC * Configure linear dependencies between tasks using the Databricks Workflows UI

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

# MAGIC %run ./Includes/Classroom-Setup-2L

# COMMAND ----------

# MAGIC %md
# MAGIC ## B. Generate Job Configuration
# MAGIC 1. Run the cell below to print out the values you'll use to configure your pipeline in subsequent steps. Make sure to specify the correct job name and notebooks.

# COMMAND ----------

DA.print_job_config(
    job_name_extension='Lesson_02',
    notebook_paths='/Task Notebooks/Lesson 2 Notebooks',
    notebooks=[
        '2.01 - Ingest CSV',
        '2.02 - Create Invalid Region Table',
        '2.02 - Create Valid Region Table'
    ],
    job_tasks={
        'Ingest_CSV': [],
        'Create_Invalid_Region_Table': ['Ingest_CSV'],
        'Create_Valid_Region_Table': ['Ingest_CSV']
    },
    check_task_dependencies = True
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Configure a Job With Multiple Tasks
# MAGIC The job will complete three simple tasks:
# MAGIC
# MAGIC 1. (Notebook #1) Ingest a CSV file and create the **customers_bronze** table in your schema.
# MAGIC 2. (Notebook #2) Create a table called **customers_invalid_region** in your schema.
# MAGIC 3. (Notebook #3) Create a table called **customers_valid_region** in your schema.

# COMMAND ----------

# MAGIC %md
# MAGIC ### C1. Add a Single Notebook Task
# MAGIC
# MAGIC Let's start by scheduling the first notebook [./Task Notebooks/Lesson 2 Notebooks/2.01 - Ingest CSV]($./Task Notebooks/Lesson 2 Notebooks/2.01 - Ingest CSV) notebook. Click the hotlink in previous sentence to review the code.
# MAGIC
# MAGIC The notebook creates a table named **customers_bronze** in your schema from the CSV file in the volume */Volumes/dbacademy_retail/v01/source_files/customers.csv*. 
# MAGIC
# MAGIC 1. Right click on the **Jobs and Pipelines** button on the sidebar and select *Open Link in New Tab*. 
# MAGIC
# MAGIC 2. Select the **Jobs & Pipeline** tab, and then click the **Create** button and **choose Job from the dropdown**.
# MAGIC
# MAGIC 3. In the top-left of the screen, enter the **Job Name** provided above to add a name for the job (must use the job name specified above).
# MAGIC
# MAGIC 4. Configure the task as specified below. You'll need the values provided in the cell output above for this step.
# MAGIC
# MAGIC
# MAGIC | Setting | Instructions |
# MAGIC |--|--|
# MAGIC | Task name | Enter **Ingest_CSV** |
# MAGIC | Type | Choose **Notebook** |
# MAGIC | Source | Choose **Workspace** |
# MAGIC | Path | Use the navigator to specify the **Notebook #1** path provided above (notebook **Task Notebooks/Lesson 2 Notebooks/2.01 - Ingest CSV**) |
# MAGIC | Compute | From the dropdown menu, select a **Serverless** cluster (We will be using Serverless clusters for jobs in this course. You can also specify a different cluster if required outside of this course) |
# MAGIC
# MAGIC **NOTE**: When selecting your all-purpose cluster, you may get a warning about how this will be billed as all-purpose compute. Production jobs should always be scheduled against new job clusters appropriately sized for the workload, as this is billed at a much lower rate.
# MAGIC <br>
# MAGIC
# MAGIC ![Job Demo 1](./Includes/images/Lesson02_Lab_OneTask.png)
# MAGIC
# MAGIC 5. Click the **Create task** button.
# MAGIC
# MAGIC 6. Click the blue **Run now** button in the top right to start the job.
# MAGIC
# MAGIC 7. Select the **Runs** tab in the navigation bar and verify that the job completes successfully.
# MAGIC
# MAGIC ![Job Demo 1](./Includes/images/Lesson02_Lab_OneTaskSuccess.png)
# MAGIC
# MAGIC 8. From **Catalog**, navigate to your schema in the **dbacademy** catalog and confirm the table **customers_bronze** was created (you might have refresh your schema).

# COMMAND ----------

# MAGIC %md
# MAGIC ### C2. Add the Second Task to the Job
# MAGIC
# MAGIC Now, configure a second task that depends on the first task, **Ingest_CSV** successfully completing. The second task will be the notebook [./Task Notebooks/Lesson 2 Notebooks/2.02 - Create Invalid Table]($./Task Notebooks/Lesson 2 Notebooks/2.02 - Create Invalid Region Table). Open the notebook and review the code.
# MAGIC
# MAGIC The notebook creates a table named **customers_invalid_region** in your schema from the **customers_bronze** table created from the previous task.
# MAGIC
# MAGIC Steps:
# MAGIC 1. Go back to your job. On the Job details page, click the **Tasks** tab.
# MAGIC
# MAGIC 2. Click the blue **+ Add task** button at the center bottom of the screen and select **Notebook** in the dropdown menu.
# MAGIC
# MAGIC 3. Configure the task:
# MAGIC
# MAGIC | Setting | Instructions |
# MAGIC |--|--|
# MAGIC | Task name | Enter **Create_Invalid_Region_Table** |
# MAGIC | Type | Choose **Notebook** |
# MAGIC | Source | Choose **Workspace** |
# MAGIC | Path | Use the navigator to specify the **Notebook #2** path provided above (notebook **Task Notebooks/Lesson 2 Notebooks/2.02 - Create Invalid Region Table**) |
# MAGIC | Compute | From the dropdown menu, select a **Serverless** cluster (We will be using Serverless clusters for jobs in this course. You can also specify a different cluster if required outside of this course) |
# MAGIC | Depends on | Verify **Ingest_CSV** (the previous task we defined) is listed |
# MAGIC
# MAGIC <br>
# MAGIC
# MAGIC 4. Click the blue **Create task** button
# MAGIC
# MAGIC <br></br>
# MAGIC ![Job Demo 1](./Includes/images/Lesson02_Lab_TwoTasks.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ### C3. Add the Third Task to the Job
# MAGIC
# MAGIC Now, configure a third task that depends on the **Ingest_CSV** successfully completing. The third task will be the notebook [./Task Notebooks/Lesson 2 Notebooks/2.03 - Create Valid Table]($./Task Notebooks/Lesson 2 Notebooks/2.02 - Create Valid Region Table). 
# MAGIC
# MAGIC The notebook creates a table named **customers_valid_region** in your schema from the **customers_bronze** table created from the first task.
# MAGIC
# MAGIC Steps:
# MAGIC 1. On the Job details page, confirm you are on the **Tasks** tab.
# MAGIC
# MAGIC 2. Click on the **Ingest_CSV** tasks.
# MAGIC
# MAGIC 3. Click the blue **+ Add task** button at the center bottom of the screen and select **Notebook** in the dropdown menu.
# MAGIC
# MAGIC 4. Configure the task:
# MAGIC
# MAGIC | Setting | Instructions |
# MAGIC |--|--|
# MAGIC | Task name | Enter **Create_Valid_Region_Table** |
# MAGIC | Type | Choose **Notebook** |
# MAGIC | Source | Choose **Workspace** |
# MAGIC | Path | Use the navigator to specify the **Notebook #3** path provided above (notebook **Task Notebooks/Lesson 2 Notebooks/2.02 - Create Valid Region Table**) |
# MAGIC | Compute | From the dropdown menu, select a **Serverless** cluster (We will be using Serverless clusters for jobs in this course. You can also specify a different cluster if required outside of this course) |
# MAGIC | Depends on | Remove current **Depends on** task and replace with **Ingest_CSV** (the previous task we defined) is listed |
# MAGIC
# MAGIC 5. Click the blue **Create task** button
# MAGIC
# MAGIC <br></br>
# MAGIC ![Job Demo 1](./Includes/images/Lesson02_Lab_ThreeTasks.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ## D. Verify the Job is Configured Correctly
# MAGIC Run the cell below to check if you configured the job correctly. Modify any errors. 
# MAGIC
# MAGIC **NOTE:** Errors include naming inconsistencies. If an error is returned and the job is setup it correctly it still should run. Feel free to try it and view the job run.

# COMMAND ----------

DA.validate_job_config()

# COMMAND ----------

# MAGIC %md
# MAGIC ## E. Run the Job
# MAGIC 1. Click the blue **Run now** button in the top right to run this job. It should take a few minutes to complete.
# MAGIC
# MAGIC 2. From the **Runs** tab, you will be able to click on the start time for this run under the **Active runs** section and visually track task progress.
# MAGIC
# MAGIC 3. On the **Runs** tab confirm that the job completed successfully.
# MAGIC
# MAGIC <br></br>
# MAGIC ![Job Demo 1](./Includes/images/Lesson02_Lab_SuccessRun.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ## F. View the New Tables
# MAGIC 1. In the left pane, select **Catalog**.
# MAGIC
# MAGIC 2. Expand the **dbacademy** catalog.
# MAGIC
# MAGIC 3. Expand your unique schema name.
# MAGIC
# MAGIC 4. Confirm that the job created the following tables:
# MAGIC   - **customers_bronze**
# MAGIC   - **customers_invalid_region**
# MAGIC   - **customers_valid_region**

# COMMAND ----------

# MAGIC %md
# MAGIC You can also use the `SHOW TABLES` statement to view available tables in your schema.

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES;

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>