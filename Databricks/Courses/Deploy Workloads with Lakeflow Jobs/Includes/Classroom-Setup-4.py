# Databricks notebook source
# MAGIC %run ./Classroom-Setup-Common

# COMMAND ----------

@DBAcademyHelper.add_method
def create_job_lesson04(self):
    '''
    Create the starter job for this demonstration.
    '''
  
    from databricks.sdk.service import jobs

    ## Set job name
    l4_job_name = f"{self.schema_name}_Lesson_04"

    ## Check if the job is already created. If the job name is already found, return an error.
    for job in self.workspace.jobs.list():
        if job.settings.name == l4_job_name:
            assert_false = False
            assert assert_false, f'You already have job named {l4_job_name}. Please go to the Jobs page and manually delete the job. Then rerun this program to recreate it from the start of this demonstration.'

    ## Set notebook path
    current_folder_path = dbutils.entry_point.getDbutils().notebook().getContext().notebookPath().getOrElse(None)

    notebook_path = "/Workspace" + "/".join(current_folder_path.split("/")[:-1]) + '/' + 'Task Notebooks/Lesson 4 Notebooks'


    ##
    ## Set job tasks
    ##
    ingest_source_1_notebook = f"{notebook_path}/Ingest Source 1"
    ingest_source_1_task = jobs.Task(
                                task_key="Ingest_Source_1",
                                notebook_task=jobs.NotebookTask(notebook_path=ingest_source_1_notebook))

    ingest_source_2_notebook = f"{notebook_path}/Ingest Source 2"
    ingest_source_2_task = jobs.Task(
                                task_key="Ingest_Source_2",
                                notebook_task=jobs.NotebookTask(notebook_path=ingest_source_2_notebook))

    ingest_source_3_notebook = f"{notebook_path}/Ingest Source 3"
    ingest_source_3_task = jobs.Task(
                                task_key="Ingest_Source_3",
                                notebook_task=jobs.NotebookTask(notebook_path=ingest_source_3_notebook))

    ## Create job
    created_job = self.workspace.jobs.create(name=l4_job_name, tasks=[ingest_source_1_task,ingest_source_2_task,ingest_source_3_task])

    ## Print success
    print(f'Created the job: {l4_job_name}\nJob ID: {created_job.job_id}')

# COMMAND ----------

DA = DBAcademyHelper()
DA.init()