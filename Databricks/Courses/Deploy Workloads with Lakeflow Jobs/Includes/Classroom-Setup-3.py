# Databricks notebook source
# MAGIC %run ./Classroom-Setup-Common

# COMMAND ----------

@DBAcademyHelper.add_method
def create_job_lesson03(self):
    '''
    Creates the starter job for each user for this demonstration.
    '''

    from databricks.sdk.service import jobs

    ## Set job name
    l3_job_name = f"{self.schema_name}_Lesson_03"

    ## Check if the job is already created. If the job name is already found, return an error.
    for job in self.workspace.jobs.list():
        if job.settings.name == l3_job_name:
            assert_false = False
            assert assert_false, f'You already have job named {l3_job_name}. Please go to the Jobs page and manually delete the job. Then rerun this program to recreate it from the start of this demonstration.'

    ## Set notebook path
    current_folder_path = dbutils.entry_point.getDbutils().notebook().getContext().notebookPath().getOrElse(None)

    notebook_path = "/Workspace" + "/".join(current_folder_path.split("/")[:-1]) + '/' + 'Task Notebooks/Lesson 3 Notebooks/View Baby Names'

    ## Set job task
    task_1 = jobs.Task(
        task_key="View_New_CSV_Data",
        notebook_task=jobs.NotebookTask(notebook_path=notebook_path),
    )

    ## Create job
    created_job = self.workspace.jobs.create(name=l3_job_name, tasks=[task_1])

    ## Print success
    print(f'Created the job: {l3_job_name}\nJob ID: {created_job.job_id}')

# COMMAND ----------

@DBAcademyHelper.add_method
def delete_baby_names_csv(self):
    '''
    Deletes the babynames.csv file if it exists to redo the demo.
    '''
    path_to_your_baby_names_csv = (f"/Volumes/{self.catalog_name}/{self.schema_name}/trigger_storage_location/babynames.csv")
    dbutils.fs.rm(f'{path_to_your_baby_names_csv}')
    print(f'If the file exists, deleted the {path_to_your_baby_names_csv} file.')

# COMMAND ----------

DA = DBAcademyHelper()
DA.init()

DA.display_config_values([('Course Catalog',DA.catalog_name),('Your Schema',DA.schema_name)])