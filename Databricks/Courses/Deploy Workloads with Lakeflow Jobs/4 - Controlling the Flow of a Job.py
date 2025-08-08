# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # 4 - Controlling the Flow of a Job
# MAGIC
# MAGIC Databricks Jobs have the ability to run tasks based on the result of previously run tasks. For example, you can setup a task to only run if a previous task fails.
# MAGIC
# MAGIC Also, when a task fails, you can repair the run and restart tasks without restarting the whole job. This can save a significant amount of time.
# MAGIC
# MAGIC In this lesson, we will configure a pipeline with conditional logic, and we will learn how to repair runs. 
# MAGIC
# MAGIC **Our goal is to create this job:**
# MAGIC
# MAGIC ![Lesson04_FullJobRun](./Includes/images/Lesson04_FullJobRun.png)

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

# MAGIC %run ./Includes/Classroom-Setup-4

# COMMAND ----------

# MAGIC %md
# MAGIC ## B. Create a Starter Job

# COMMAND ----------

# MAGIC %md
# MAGIC 1. Run the cell below to use the custom `DA` object to create a starter job for this demonstration. After the cell completes, it will create a job named **&lt;your-schema>_Lesson_04&gt;** with three individual tasks.
# MAGIC
# MAGIC **NOTE:** The following custom method uses the Databricks SDK to programmatically create a job for demonstration purposes. You can find the method definition that uses the Databricks SDK to create the job in the [Classroom-Setup-Common]($./Includes/Classroom-Setup-Common) notebook. However, the [Databricks SDK](https://databricks-sdk-py.readthedocs.io/en/latest/) is outside the scope of this course.

# COMMAND ----------

DA.create_job_lesson04()

# COMMAND ----------

# MAGIC %md
# MAGIC 2. Open your new starter job **&lt;your-schema>_Lesson_04&gt;**:
# MAGIC    
# MAGIC    a. Navigate to **Jobs and Pipelines** and open it in a new tab.
# MAGIC     
# MAGIC    b. Select your new job, **&lt;your-schema>_Lesson_04&gt;**.
# MAGIC     
# MAGIC    c. Select **Tasks** in the top navigation bar.
# MAGIC     
# MAGIC    d. View your job. Notice that the job contains three tasks: **Ingest_Source_1**, **Ingest_Source_2**, and **Ingest_Source_3**. The three tasks should all be independent of one another. 
# MAGIC
# MAGIC    e. Leave the job open and return to these instructions.
# MAGIC
# MAGIC ![Lesson04_DefaultJob](./Includes/images/Lesson04_DefaultJob.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Explore the Task Notebooks
# MAGIC 1. The following notebooks use simple code to demonstrate the functionality of creating orchestrated jobs. Each notebook is in **Task Notebooks** > **Lesson 4 Notebooks**. You can use the links below to view each notebook used in the tasks and explore the code.
# MAGIC
# MAGIC     - Task: [./Task Notebooks/Lesson 4/Ingest_Source_1]($./Task Notebooks/Lesson 4 Notebooks/Ingest Source 1) notebook
# MAGIC
# MAGIC     - Task: [./Task Notebooks/Lesson 4/Ingest_Source_2]($./Task Notebooks/Lesson 4 Notebooks/Ingest Source 2) notebook
# MAGIC
# MAGIC     - Task: [./Task Notebooks/Lesson 4/Ingest_Source_3]($./Task Notebooks/Lesson 4 Notebooks/Ingest Source 3) notebook

# COMMAND ----------

# MAGIC %md
# MAGIC ## D. Set Dependencies on the Tasks
# MAGIC We are going to make some changes to this job and configure our main task to run only if all previous tasks succeed.
# MAGIC
# MAGIC To simulate a real-world scenario, we will configure the job to either succeed or fail based on a task parameter. At this point, we want to observe the behavior when an upstream task fails, so we will configure the task parameter to intentionally cause the notebook to fail.

# COMMAND ----------

# MAGIC %md
# MAGIC ### D1. Add a Parameter to the Ingest_Source_1 Task
# MAGIC
# MAGIC Configure the task parameter in the **Ingest_Source_1** task as follows:
# MAGIC
# MAGIC 1. Select the task **Ingest_Source_1**.
# MAGIC
# MAGIC 2. In the **Parameters** field, click **Add**.
# MAGIC
# MAGIC 3. For **Key**, type *test_value*.
# MAGIC
# MAGIC 4. For **Value**, type *Failure*.
# MAGIC
# MAGIC     **NOTE:** Be aware values are case-sensitive
# MAGIC
# MAGIC 5. For **Retries**, select the edit button. In the **Retry Policy**, deselect *Enable serverless auto-optimization (may include at most 3 retries)*. This will turn off the retry policy if the job fails, preventing the task from running multiple times to save time during the demonstration.
# MAGIC
# MAGIC 6. Click **Confirm**.
# MAGIC
# MAGIC 5. Click **Save task**.
# MAGIC
# MAGIC We now added a parameter to the **Ingest_Source_1** task. 
# MAGIC
# MAGIC **The parameter value  *Failure* will cause an error when this notebook is run.**

# COMMAND ----------

# MAGIC %md
# MAGIC ### D2. Add the Clean_Data Task
# MAGIC Let's add the **Clean Data** notebook as a task named **Clean_Data**. The notebook will add dynamic value references to the task. 
# MAGIC
# MAGIC Databricks Lakeflow Jobs provide [options](https://docs.databricks.com/en/workflows/jobs/parameter-value-references.html) for passing information about jobs/tasks to tasks and from one task to another. 
# MAGIC
# MAGIC
# MAGIC 1. Open and explore the code in the [./Task Notebooks/Lesson 4/Clean Data]($./Task Notebooks/Lesson 4 Notebooks/Clean Data) notebook.
# MAGIC
# MAGIC     **NOTE:** The notebook sets a task value in a notebook using `dbutils.jobs.taskValues.set(key = 'bad_records', value = 5)`. This dynamically creates a **Key** named *bad_records* with the **Value** *5*. This can be set dynamically in whatever way you wish.
# MAGIC
# MAGIC     - [Set task values](https://docs.databricks.com/aws/en/jobs/task-values#set-task-values) documentation
# MAGIC
# MAGIC
# MAGIC 1. Close the **Clean Data** notebook.
# MAGIC
# MAGIC 1. Click **Add task**, and select **Notebook**. 
# MAGIC
# MAGIC 1. Name the task **Clean_Data**.
# MAGIC
# MAGIC 1. Click the path field, select the notebook, **Lesson 4 Notebooks/Clean Data**, and click **Confirm**
# MAGIC
# MAGIC 1. Click the **Depends on** field, and select all three of the tasks in the job (**Ingest_Source_1**, **Ingest_Source_2**, **Ingest_Source_3** ) to add them to the list. The DAG should show connections from the first three tasks to the **Clean_Data** task.
# MAGIC
# MAGIC 1. Click **All succeeded** in the **Run if dependencies** field to drop open the combo box. Note the variety of conditions available. 
# MAGIC
# MAGIC 1. Select **All succeeded**.
# MAGIC
# MAGIC 1. Click **Create Task**.
# MAGIC
# MAGIC ![Lesson04_Clean_Data_Task](./Includes/images/Lesson04_Clean_Data_Task.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ### D3. Run the Job
# MAGIC 1. Run the job by clicking **Run now** in the upper-right corner. 
# MAGIC
# MAGIC 2. A pop-up window appears with a link to the job run. Click **View run**.
# MAGIC
# MAGIC 3. Watch the tasks in the DAG. The colors change to show the progress of the task (about 2-3 minutes to complete):
# MAGIC
# MAGIC     * **Gray** -- the task has not started
# MAGIC     * **Green stripes** -- the task is currently running
# MAGIC     * **Solid green** -- the task completed successfully
# MAGIC     * **Dark red** -- the task failed
# MAGIC     * **Light red** -- an upstream task failed, so the current task never ran
# MAGIC
# MAGIC 4. When the run is finished, note that **Ingest_Source_1** failed. This was expected. Also, note that our **Clean_Data** task never ran because we required that all three parent tasks must succeed before the **Clean_Data** task will run.
# MAGIC
# MAGIC ![Lesson04_Ingest_Source_1_Failure](./Includes/images/Lesson04_Ingest_Source_1_Failure.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ### D4. Repairing Job Runs
# MAGIC
# MAGIC We have the ability to view the notebooks used in a task, including their output, as part of the job run. This can help us diagnose errors. We also have the ability to re-run specific tasks in a failed job run. 
# MAGIC
# MAGIC Consider the following example:
# MAGIC
# MAGIC You are developing a job that includes a handful of notebooks. During a run of the job, one of the tasks fails. You can change the code in that notebook and re-run that task and any tasks that depend on it. Additionally, you can change task parameters and re-run a task. Let's do this now:
# MAGIC
# MAGIC 1. In the upper-right corner, click **Repair run**. 
# MAGIC
# MAGIC 2. Make sure the **Ingest_Source_1** task is selected. Change the value for **test_value** from *Failure* to *Succeed*.
# MAGIC
# MAGIC 3. Highlight **Clean_Data** task so it is included in the Repair Run, then click **Repair run (2)** and let the job complete. You'll see Pipeline animate if a few seconds.
# MAGIC
# MAGIC 4. The "2" in the **Repair run** button indicates that Databricks selected both the failed task and the task that depended on it. You can select and deselect whichever tasks you wish to re-run.
# MAGIC
# MAGIC     **NOTE:** When we use **Repair run** to change a parameter, the original parameter in the task definition is not changed—only the parameter in the current run is updated. In next Step, we will hard-code the Task parameter from *Failure* to *Succeed*.
# MAGIC
# MAGIC 5. After the repaired run is executed successfully complete the following:
# MAGIC     - a. Navigate back to the job by selecting it in the link above the job name
# MAGIC     
# MAGIC     - b. Select **Tasks** in the navigation bar.
# MAGIC     
# MAGIC     - c. Select the **Ingest_Source_1** task and modify the parameter value of **test_value** to **Succeed**
# MAGIC     
# MAGIC     - d. Then select **Save task**.
# MAGIC
# MAGIC
# MAGIC ![Lesson04_RepairRun_01](./Includes/images/Lesson04_RepairRun_01.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ## E. Add If/Else Condition Task
# MAGIC We can also perform branching logic based on a boolean condition. Let's see an example of this in action. 
# MAGIC
# MAGIC Suppose our **Clean_Data** task pushes bad records to a quarantine table. We will want to fix these bad records, if possible, before continuing to the next task. Let's set up this logic:
# MAGIC
# MAGIC 1. Go back to the job definition page for our job and make sure you are on the **Tasks** tab.
# MAGIC
# MAGIC 2. Select the **Clean_Data** task and click **Add task**. Then select **If/else condition** (under the **Control flow** section at the bottom of the list).
# MAGIC
# MAGIC 3. Name the task **Is_Record_Check_0**. Notice that you have 2 new settings in the node (*True* and *False*).
# MAGIC
# MAGIC 4. For the condition field complete the following:
# MAGIC     - a. Type `{{tasks.Clean_Data.values.bad_records}}` (make sure to include both sets of curly brace) in the left-hand side field.  
# MAGIC
# MAGIC     - b. Choose **`==`** in the dropdown, and type *0* in the right-hand side field. This code obtains the value of the **bad_records** key in the **Clean_Data** task and compares it to the condition.
# MAGIC
# MAGIC     **NOTE:** To obtain the task value with the key *value_name* that was set by task *task_name* use the following:`{{tasks.task_name.values.value_name}}`. View the [Supported value references](https://docs.databricks.com/en/jobs/dynamic-value-references.html#supported-value-references) for a list of dynamic value references that are supported.
# MAGIC
# MAGIC 5. Ensure **Depends on** is set to **Clean_Data** and **Run if dependencies** is set to **All succeeded**.
# MAGIC
# MAGIC 6. Click **Save task**.
# MAGIC
# MAGIC ![Lesson04_If_Condition](./Includes/images/Lesson04_If_Condition.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ### E1. Setting Our "False" Task
# MAGIC Let's setup a task that will fix bad records before moving on in the job. That is, if the **bad_records** value is not equal to *0*.:
# MAGIC
# MAGIC 1. Select the **Is_Record_Check_0** task and select **Add task** on the job definition page, then select **Notebook**.
# MAGIC
# MAGIC 1. Name the task **Fix_Bad_Records**.
# MAGIC
# MAGIC 1. For the path, navigate to **Lesson 4 Notebooks/Fix Bad Records**. 
# MAGIC
# MAGIC     **NOTE:** The **Fix_Bad_Records** notebook will simply execute the code: `print("Logic that fixes bad records.")`. In a real world scenario you can set any logic here.
# MAGIC
# MAGIC 1. For **Depends on**, confirm only **Is_Record_Check_0 (false)**. 
# MAGIC
# MAGIC     **NOTE:** Please make sure that **Is_Record_Check_0 (true)** is not selected!
# MAGIC
# MAGIC 1. Ensure that Run if dependencies is set to **All succeeded**.
# MAGIC
# MAGIC 1. Click **Create task**
# MAGIC
# MAGIC We are setting this task to only run if the **Is_Record_Check_0** fails, meaning the value for the **bad_records** key did not equal 0. In our current scenario, the **Clean_Data** task sets the value of **bad_records** to *5*.
# MAGIC
# MAGIC
# MAGIC ![Lesson04_Fix_Bad_Records_False](./Includes/images/Lesson04_Fix_Bad_Records_False.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ### E2. Aggregate Records Task
# MAGIC Let's setup a task for aggregating data. We want this task to either run if:
# MAGIC - If the **Is_Record_Check_0** is *true* (meaning `bad_records == 0`) or 
# MAGIC - If the **Is_Record_Check_0** is *false* (meaning `bad_records != 0`) and the **Fix_Bad_Records** task completed.
# MAGIC
# MAGIC **NOTE:** The **Aggregate Records** notebook will simply run: `print("Aggregates records.")`. In a real world scenario you can add any logic you need.
# MAGIC
# MAGIC 1. Select the **Fix_Bad_Records** task then select **Add task** and select **Notebook**.
# MAGIC
# MAGIC 1. Name the task **Aggregate_Records**.
# MAGIC
# MAGIC 1. For the path, navigate to **Lesson 4 Notebooks/Aggregate Records**
# MAGIC
# MAGIC 1. For **Depends on**, select **Is_Record_Check_0 (true)** AND **Fix_Bad_Records**.
# MAGIC
# MAGIC 1. Set **Run if dependencies** to **At least one succeeded**.
# MAGIC
# MAGIC 1. Click **Create task**
# MAGIC
# MAGIC This task will run if either:
# MAGIC - **Is_Record_Check_0** is *true*, (which is not the case since 5 does not equal 0) or
# MAGIC - **Fix_Bad_Records** completed successfully (this is the case for our example)
# MAGIC
# MAGIC ![Lesson04_FullJob](./Includes/images/Lesson04_FullJob.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ### E3. Run the Entire Job
# MAGIC
# MAGIC ##### IMPORTANT NOTE
# MAGIC Before running the job, go to the **Task** tab on the **Job Details** page and select **Ingest_Source_1**. In the **Parameters** section make sure the key **test_value** is set to *Succeed*.
# MAGIC
# MAGIC 1. Click **Run now** to run the entire job. Then in the pop up select **View Run**.
# MAGIC   
# MAGIC 2. At the moment, our hard-coded **bad_records** value is set to *5*, so we should see the **Fix_Bad_Records** task run before the **Aggregate_Records** task when we run the job.
# MAGIC
# MAGIC ![Lesson04_FullJobRun](./Includes/images/Lesson04_FullJobRun.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Bonus lab: 
# MAGIC ###Change *Is_Record_Check_0* task to fire a *True* condition
# MAGIC
# MAGIC 1. From *Tasks* tab, open the  **Is_Record_Check_0** task.
# MAGIC
# MAGIC 2. In **Condition** caption change 0 to 5.  Now 5 (from **Clean_Data** task) = 5 (in this task). 
# MAGIC
# MAGIC 3. For completeness, change the *Task name* to **Is_Record_Check_5**.  This will fire the **True** condition when run and flow through to the **Aggregate_Records** task. Save the task and click on **Run now** button.
# MAGIC
# MAGIC
# MAGIC ##### Final Run
# MAGIC ![Lesson04_True_run](./Includes/images/Lesson04_True_run.png)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>