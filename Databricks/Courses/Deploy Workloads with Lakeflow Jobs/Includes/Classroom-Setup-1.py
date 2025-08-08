# Databricks notebook source
# MAGIC %run ./Classroom-Setup-Common

# COMMAND ----------

DA = DBAcademyHelper()
DA.init()

DA.display_config_values([('Course Catalog',DA.catalog_name),('Your Schema',DA.schema_name)])

# COMMAND ----------

# ## don't need this we think.
# setattr(DA, 'paths.storage_location', f'{DA.paths.working_dir}/storage_location')

# DA.dlt_data_factory = DataFactory()

# DA.dlt_data_factory.load()
# # The location that the DLT databases should be written to

# DA.dlt_data_factory = DataFactory()

# required_user_job_name = 'gigantic_attention_Lesson_01'

# ## Get a list of workspace jobs
# workspace_jobs = DA.workspace.jobs.list()

# ## Loop over available jobs to find the user's required job name if available
# for job in workspace_jobs:

#     ## Get the job name from list of jobs
#     job_name = job.settings.name

#     ## Search for the user's specified job name that they should use. If found, get the job_id
#     if job_name == required_user_job_name:
#         job_id = job.job_id
#         job_name = job_name
#         break
#     else:
#         job_name = 'Not found'

# # Validate the specific job
# assert job_name == required_user_job_name, f'Could not find a job named: {required_user_job_name}. Please name the job the that was specified in the notebook.assert' 

# ##
# ## Get the specific job information using the job_id
# ##
# job_info = DA.workspace.jobs.get(job_id)

# ## Loop over job information to get notebook used with path
# job_notebooks = job_info.settings.tasks

# list_of_notebooks_in_job = []
# for notebook in job_notebooks:
#     notebook_used = notebook.notebook_task.notebook_path

#     ## Create a list of notebooks used in this job
#     list_of_notebooks_in_job.append(notebook_used)
#     print(notebook_used)
#     print('-----')





# # assert ['abc','b'] == ['abc','a'], 'lists not the same'
# # # assert test_notebooks(), "Notebooks are not properly configured"
# # # assert len(pipeline.spec.configuration) == 1, "Expected exactly one configuration parameter."
# # # assert pipeline.spec.configuration.get("source") == config.source, f"Expected the configuration parameter {config.source}"
# # # assert pipeline.spec.development == True, "Expected the pipeline to be in Development mode."
# # # assert pipeline.spec.serverless == True, "Expected Serverless to be enabled."
# # # assert pipeline.spec.channel == "CURRENT", "Excpected the channel to be set to Current."
# # # assert pipeline.spec.continuous == False, "Expected the Pipeline mode to be Triggered."

# # print('Pipeline validation complete. No errors found.')