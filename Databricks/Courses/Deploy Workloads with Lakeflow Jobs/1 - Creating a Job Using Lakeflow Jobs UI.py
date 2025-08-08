# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # 1 - Creating a Job Using Lakeflow Jobs UI
# MAGIC
# MAGIC In this lesson, we will start by creating a job using a single notebook and exploring the Lakeflow Jobs UI.
# MAGIC
# MAGIC ## Learning Objectives
# MAGIC By the end of this lesson, you should be able to:
# MAGIC * Schedule a notebook task in a Databricks Workflow Job
# MAGIC * Describe job scheduling options and differences between cluster types
# MAGIC * Review Job Runs to track progress and see results

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
# MAGIC
# MAGIC
# MAGIC ```
# MAGIC USE CATALOG dbacademy;
# MAGIC USE SCHEMA dbacademy.<your unique schema name>;
# MAGIC ```
# MAGIC
# MAGIC **NOTE:** The `DA` object is only used in Databricks Academy courses and is not available outside of these courses. It will dynamically reference the information needed to run the course.

# COMMAND ----------

# MAGIC %run ./Includes/Classroom-Setup-1

# COMMAND ----------

# MAGIC %md
# MAGIC ## B. Explore Your Schema
# MAGIC 1. Expand the course catalog **dbacademy** on the left.
# MAGIC
# MAGIC 2. Expand your unique schema name using the information from the above cell. Please remember your schema name.
# MAGIC
# MAGIC 3. Notice that within your schema no tables exist.

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Generate Job Configuration
# MAGIC
# MAGIC 1. Run the cell below to print out values you'll use to configure your job in subsequent steps. Make sure to specify the correct job name and notebooks.
# MAGIC
# MAGIC **NOTE:** The `DA.print_job_config` object is specific to the Databricks Academy course. It will output the necessary information to help you create the job.

# COMMAND ----------

DA.print_job_config(job_name_extension='Lesson_01', 
                    notebook_paths='/Task Notebooks/Lesson 1 Notebooks',
                    notebooks=['1.01 - Create Simple Table'])

# COMMAND ----------

# MAGIC %md
# MAGIC ## D. Configure Job with a Single Notebook Task
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ### D1. View the Notebook
# MAGIC 1. Select the link to open the [./Task Notebooks/Lesson 1/1.01 - Create Simple Table]($./Task Notebooks/Lesson 1 Notebooks/1.01 - Create Simple Table) notebook. Examine the notebook and notice that it will create a simple table named **lesson1_workflow_users** in your specified schema.
# MAGIC
# MAGIC 2. Close the tab after the code has been reviewed and return to this notebook.

# COMMAND ----------

# MAGIC %md
# MAGIC ### D2. Configure the Job
# MAGIC When using the Jobs UI to orchestrate a workload with multiple tasks, you'll always begin by creating a job with a single task.
# MAGIC
# MAGIC Steps:
# MAGIC 1. Right click on the **Jobs and Pipelines** button on the sidebar and select *Open Link in New Tab*. 
# MAGIC
# MAGIC 2. Select the **Jobs & Pipeline** tab, and then click the **Create** button and **choose Job from the dropdown**.
# MAGIC
# MAGIC 3. In the top-left of the screen, enter the **Job Name** provided above to add a name for the job (must use the job name specified above).
# MAGIC
# MAGIC 4. Configure the task as specified below. You'll need the values provided in the cell output above for this step.
# MAGIC
# MAGIC | Setting | Instructions |
# MAGIC |--|--|
# MAGIC | Task name | Enter the task name **create_table** |
# MAGIC | Type | Choose **Notebook** |
# MAGIC | Source | Choose **Workspace** |
# MAGIC | Path | Use the navigator to specify the **Notebook #1** path above (**1.01 - Create Simple Table**) |
# MAGIC | Compute | From the dropdown menu, select a **Serverless** cluster (We will be using Serverless clusters for jobs in this course. You can also specify a different cluster if required outside of this course) |
# MAGIC | Create task | Click **Create task** |
# MAGIC |Performance optimized mode (in Job Detail) | **Turn on**|
# MAGIC
# MAGIC **NOTE: Performance optimized mode** 
# MAGIC - **Performance-optimized mode**
# MAGIC Fast, performant compute startup and execution speed.
# MAGIC
# MAGIC - **Standard mode**
# MAGIC Disabling performance optimization gives you startup times similar to Classic infrastructure and reduces your cost.
# MAGIC
# MAGIC
# MAGIC <br>
# MAGIC
# MAGIC **NOTE**: If you selected your all-purpose cluster, you may get a warning about how this will be billed as all-purpose compute. Production jobs should always be scheduled against new job clusters appropriately sized for the workload, as this is billed at a much lower rate.
# MAGIC
# MAGIC
# MAGIC ![Job Demo 1](./Includes/images/Lesson01_CreateJob.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ## E. Run the Job
# MAGIC
# MAGIC 1. In the upper-right corner, click the blue **Run now** button in the top right to start the job.
# MAGIC
# MAGIC **NOTE:** When you start the job run, you can click the link and view the run. However, let's look at another way you can view past, and current, job runs.

# COMMAND ----------

# MAGIC %md
# MAGIC ## F. Review the Job Run
# MAGIC
# MAGIC
# MAGIC 1. On the Job Details page, select the **Runs** tab in the top-left of the screen (you should currently be on the **Tasks** tab)
# MAGIC
# MAGIC 2. Open the output details by clicking on the timestamp field under the **Start time** column
# MAGIC     - If **the job is still running**, you will see the active state of the notebook with a **Status** of **`Pending`** or **`Running`** in the right side panel. 
# MAGIC     - If **the job has completed**, you will see the full execution of the notebook with a **Status** of **`Succeeded`** or **`Failed`** in the right side panel
# MAGIC
# MAGIC *Example*
# MAGIC
# MAGIC ![Job Demo 1](./Includes/images/Lesson01_JobRun.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ## G. View Your New Table
# MAGIC 1. From left-hand pane, select **Catalog**. Then drill down from **dbacademy** catalog.
# MAGIC
# MAGIC 2. Expand your unique schema name.
# MAGIC
# MAGIC 3. Notice that within your schema a table named **lesson1_workflow_users** was created from the job.

# COMMAND ----------

# MAGIC %md
# MAGIC [Lakeflow Jobs Documentation](https://docs.databricks.com/aws/en/jobs/)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>