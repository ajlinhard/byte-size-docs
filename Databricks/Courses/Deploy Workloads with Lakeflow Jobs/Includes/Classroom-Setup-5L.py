# Databricks notebook source
# MAGIC %run ./Classroom-Setup-Common

# COMMAND ----------

@DBAcademyHelper.add_method
def create_job_lesson05(self):
    '''
    Create started job for lesson 05 demonstration.
    '''

    from databricks.sdk.service import jobs

    ## Set job name
    l5_job_1 = f"{self.schema_name}_Lesson_5_Job_1"
    l5_job_2 = f"{self.schema_name}_Lesson_5_Job_2"
    l5_job_3 = f"{self.schema_name}_Lesson_5_Job_3"

    ## Check if the job is already created. If the job name is already found, return an error.
    for job in self.workspace.jobs.list():
        if job.settings.name in [l5_job_1,l5_job_2,l5_job_3]:
            assert_false = False
            assert assert_false, f'You already have job named created{job.setting.name}. Please go to the Jobs page and manually delete the job. Then rerun this program to recreate it from the start of this demonstration.'

    ## Set notebook path
    current_folder_path = dbutils.entry_point.getDbutils().notebook().getContext().notebookPath().getOrElse(None)
    notebook_path = "/Workspace" + "/".join(current_folder_path.split("/")[:-1]) + '/' + 'Task Notebooks/Lesson 5 Notebooks'


    ingest_source_1_notebook = f"{notebook_path}/Ingest Source 1"
    ingest_source_1_task = jobs.Task(
                                task_key="Ingest_Source_1",
                                notebook_task=jobs.NotebookTask(notebook_path=ingest_source_1_notebook))
    
    ingest_source_2_notebook = f"{notebook_path}/Ingest Source 2"
    ingest_source_2_task = jobs.Task(
                                task_key="Ingest_Source_2",
                                notebook_task=jobs.NotebookTask(notebook_path=ingest_source_2_notebook))
    
    clean_data_notebook = f"{notebook_path}/Clean Data"
    clean_data_notebook = jobs.Task(
                                task_key="Clean_Data",
                                notebook_task=jobs.NotebookTask(notebook_path=clean_data_notebook))

    ## Create job and Priting JobId
    created_job_l5_job_1 = self.workspace.jobs.create(name=l5_job_1, tasks=[ingest_source_1_task])
    print(f'Created the job: {l5_job_1}\nJob ID: {created_job_l5_job_1.job_id}')

    created_job_l5_job_2 = self.workspace.jobs.create(name=l5_job_2, tasks=[ingest_source_2_task])
    print(f'Created the job: {l5_job_2}\nJob ID: {created_job_l5_job_2.job_id}')

    created_job_l5_job_3 = self.workspace.jobs.create(name=l5_job_3, tasks=[clean_data_notebook])
    print(f'Created the job: {l5_job_3}\nJob ID: {created_job_l5_job_3.job_id}')

# COMMAND ----------

DA = DBAcademyHelper()
DA.init()

DA.display_config_values([('Course Catalog',DA.catalog_name),('Your Schema',DA.schema_name)])

# The location that the DLT databases should be written to????
# setattr(DA, 'paths.storage_location', f'{DA.paths.working_dir}/storage_location')