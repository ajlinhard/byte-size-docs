# Databricks notebook source
# MAGIC %run ../../Includes/_common

# COMMAND ----------

@DBAcademyHelper.add_method
def print_job_config(self, job_name_extension, notebook_paths, notebooks, job_tasks=None, check_task_dependencies=False):
    """
    - Prints an HTML output in the cell below with information about the Job Name and notebooks to use with the path for each user.
    - Method also sets the required job name, job notebooks, and tasks in the DA object as attributes to use for validation testing.

    Parameters:
        - job_name_extension (str): Specify what you want your job name extension to be: (schema_{job_name_extension}).
        - notebook_paths (str): Uses the a folder where the executing program lives.
            Example: /Task Notebooks/Lesson 1 Notebooks
        - notebooks (list[str]) : List of notebook names in the notebook_paths folder location
            Example: ['01-reset','02-ingest']
        - job_task_names (dict{'task':[list of dependencies]}) : Dictionary of the required task names for the job and their dependencies as a dictionary. Leave as None if you do not want to check the tasks.
            Example:
                job_tasks={
                    'Ingest_CSV': [],
                    'Create_Invalid_Table': ['Ingest_CSV'],
                    'Create_Valid_Table': ['Ingest_CSV','Create_Invalid_Table']
                }
        - check_task_dependencies (boolean) : Determines whether to check for dependencies in job tasks. Leave as False if you don't want to check the dependencies.

    Returns:
        - Return HTML output with the specified string information
        - Attributes
            - user_required_job_name that holds the required job name
            - user_reuqired_job_notebooks that holds a list of required notebooks
            - user_required_job_task_names = job tasks and dependencies
            - check_task_dependencies = value if needs to check for dependencies

    Example:
        DA.print_job_config(
            job_name_extension='Lesson_02',
            notebook_paths='/Task Notebooks/Lesson 2 Notebooks',
            notebooks=[
                '2.01 - Ingest CSV',
                '2.02 - Create Invalid Table',
                '2.02 - Create Valid Table'
            ],
            job_tasks={
                'Ingest_CSV': [],
                'Create_Invalid_Table': ['Ingest_CSV'],
                'Create_Valid_Table': ['Ingest_CSV','Create_Invalid_Table']
            },
            check_task_dependencies = True
        )
    """

    ## Get current path of notebook
    base_path = dbutils.entry_point.getDbutils().notebook().getContext().notebookPath().getOrElse(None)

    ## Concatenates the schema name of the user with the job name
    required_job_name = f"{self.schema_name}_{job_name_extension}"

    ## Goes back two paths to main course folder
    main_course_folder_path = "/Workspace" + "/".join(base_path.split("/")[:-1]) + notebook_paths + '/'

    ## Create paths for each notebook specified in method argument notebooks(list of notebooks to use)
    notebooks_to_print = []
    for i, notebook in enumerate(notebooks):
        current_notebook_path = (f'Notebook #{i + 1}', main_course_folder_path + notebook)
        notebooks_to_print.append(current_notebook_path)


    ## Use the display_config_values function to display the following values as HTML output.
    ## Will list the Job Name and notebook paths.
    self.display_config_values([
            ('Job Name', required_job_name)
        ] + notebooks_to_print)
    
    ## Store the current job name, notebooks to use, tasks and if to check task dependencies.
    self.user_required_job_name = required_job_name
    self.user_required_job_notebooks = [item[1] for item in notebooks_to_print]
    self.user_required_job_task_names = job_tasks
    self.check_task_dependencies = check_task_dependencies

# COMMAND ----------

@DBAcademyHelper.add_method
def get_job_id(self):
    '''
    Searches for the required job name from the print_job_config method. 

    Returns:
        - If found returns the job id as an attribute named current_job_id that contains the job id of the required job. Will be used to obtain job info.
        - If not found job_id = None.
    '''  
    ## Get a list of workspace jobs
    workspace_jobs = self.workspace.jobs.list()

    ## Loop over available jobs to find the user's required job name if available
    for job in workspace_jobs:

        ## Get the job name from list of jobs
        job_name = job.settings.name
        ## Search for the user's specified job name that they should use. If found, get the job_id
        if job_name == self.user_required_job_name:
            ## Store the job_id for other validation tests. If job found end if/then.
            self.current_job_id = job.job_id
            print(f'1. Required job Id has been found.')
            break
        else:
            self.current_job_id = None

# COMMAND ----------

@DBAcademyHelper.add_method
def validate_job_name(self):
    '''
    Validates the job name. If the job name is found from the get_job_id() method, current_job_id will be populated with the job id. If if it's not found current_job_id will be null and the test will return an error.
    '''
    if self.current_job_id == None :
        name_not_found = False
        assert name_not_found, f'Could not find a job named {self.user_required_job_name}. Please name the job the that was specified in the notebook.'
    else :
        print(f'2. Required job name {self.user_required_job_name} has been found.')

# COMMAND ----------

@DBAcademyHelper.add_method
def validate_job_notebooks(self):
    '''
    Validates the job notebooks. The required notebooks are set within the print_pipeline_config method in the user_required_job_notebooks attribute.
    '''
    ## Get information on current job
    job_info = self.workspace.jobs.get(self.current_job_id)

    ## Get a list of all tasks for the job
    job_tasks = job_info.settings.tasks

    ## Loop over each tasks and store notebook information
    list_of_notebooks_in_job = []
    for task in job_tasks:
        notebook_path = task.notebook_task.notebook_path
        # get_notebook_path = notebook_path.split("/Workspace",1)[1]  # Remove workspace from path

        list_of_notebooks_in_job.append(notebook_path)

    if list_of_notebooks_in_job == self.user_required_job_notebooks:
        print(f'3. Required task notebooks set correctly.')
    else:
        name_not_found = False
        assert name_not_found, f'The specified notebooks were not set correctly. Please use only the following notebooks(s):\n {self.user_required_job_notebooks}.Please view your job configuration and set the correct notebooks.'

# COMMAND ----------

@DBAcademyHelper.add_method
def validate_job_tasks(self):
    '''
    Checks the task names for the job.
    '''

    ## If None do not perform the check
    if self.user_required_job_task_names == None:
        pass
    else:
        required_job_tasks = list(self.user_required_job_task_names.keys())

        ## Get job information
        job_info = self.workspace.jobs.get(self.current_job_id)

        ## Get information about each task in the job
        job_tasks_info = job_info.settings.tasks

        ## Create a list of task names in the job
        user_job_tasks = []
        for task in job_tasks_info:
            task_key = task.task_key           ## task name
            user_job_tasks.append(task_key)    ## add to list

        ## Sort lists in case the API doesn't return in a specific order
        user_job_tasks.sort()
        required_job_tasks.sort()

        ## Lower case to avoid case issues
        user_job_tasks = [item.lower() for item in user_job_tasks]
        required_job_tasks = [item.lower() for item in required_job_tasks]

        ## If they equal each other it passes the test
        if user_job_tasks == required_job_tasks:
            print('4. Job task names set correctly.')
        else:
            name_not_found = False
            assert name_not_found, f'The specified job tasks names were not set correctly. Please review the notebook directions and name the tasks correctly.' 


        ##
        ## Check task dependencies
        ##
        if self.check_task_dependencies == False:
            pass
        else:
            user_defined_dependencies = {}

            for task in job_tasks_info:

                ## Get the task key
                task_key = task.task_key

                ## Get the dependencies for each task
                task_dependencies = task.depends_on

                ## Create a dictionary of tasks with dependencies
                user_defined_dependencies[task_key.lower()] = [dep.task_key.lower() for dep in task.depends_on]
            
            ## Lower case initial check
            user_required_job_task_names_case_insensitive = {key.lower(): [task.lower() for task in value] for key, value in self.user_required_job_task_names.items()}

            if user_defined_dependencies == user_required_job_task_names_case_insensitive:
                print('5. Task dependencies are set correctly.')
            else:
                name_not_found = False
                assert name_not_found, f'Job task dependencies are incorrectly set. Please review the notebook directions and update the dependencies accordingly.'

# COMMAND ----------

@DBAcademyHelper.add_method
def validate_job_config(self):
    '''
    Runs the job validation testing using the validate methods above.
    '''

    ## Gets job id and checks for the valid name
    self.get_job_id()

    ## Gets Job Name and check for Job Name
    self.validate_job_name()
    
    ## Gets notebooks in job and checks
    self.validate_job_notebooks()

    ## Test task names in job
    self.validate_job_tasks()

    ## If all tests pass, print the message.
    print('-------------------------------------------')
    print('Your Job has been validated. Tests passed!')

# COMMAND ----------

# @DBAcademyHelper.monkey_patch
# def get_job_config(self):
    
#     unique_name = DA.unique_name(sep="-")
#     job_name = f"{unique_name}: Example Job"
    
#     parts = dbutils.entry_point.getDbutils().notebook().getContext().notebookPath().getOrElse(None).split("/")[:-1]
#     notebook = "/".join(parts) + "/Task Notebooks/Lesson 1 Notebooks/DE 5.1.2 - Reset"
#     notebook = f"/Workspace{notebook}"

#     return JobConfig(job_name, notebook)
# 
# 
# # class JobConfig():
#     '''
#     Create a class to store the job name and specific notebooks to use for the user. This will be used in the validate method to confirm the user created the correct job name and referenced the correct notebook.
#     '''
#     def __init__(self, job_name, notebooks_to_print):
#         # The name of the pipeline
#         self.job_name = job_name

#         # This list of notebooks for this pipeline
#         self.notebook = notebooks_to_print
    
#     def __repr__(self):
#         content =  f"Name:      {self.job_name}"
#         content += f"Notebooks: {self.notebooks_to_print}"
#         return content