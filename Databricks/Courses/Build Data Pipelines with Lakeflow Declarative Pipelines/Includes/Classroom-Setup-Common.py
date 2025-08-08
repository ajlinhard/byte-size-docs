# Databricks notebook source
# MAGIC %run ../../Includes/_common

# COMMAND ----------

DA = DBAcademyHelper()
DA.init()

# COMMAND ----------

# MAGIC %sql
# MAGIC -- CREATE DA VARIABLE USING SQL FOR USER INFORMATION FROM THE META TABLE
# MAGIC
# MAGIC -- Create a temp view storing information from the obs table.
# MAGIC CREATE OR REPLACE TEMP VIEW user_info AS
# MAGIC SELECT map_from_arrays(collect_list(replace(key,'.','_')), collect_list(value))
# MAGIC FROM dbacademy.ops.meta;
# MAGIC
# MAGIC -- Create SQL dictionary var (map)
# MAGIC DECLARE OR REPLACE DA MAP<STRING,STRING>;
# MAGIC
# MAGIC -- Set the temp view in the DA variable
# MAGIC SET VAR DA = (SELECT * FROM user_info);
# MAGIC
# MAGIC DROP VIEW IF EXISTS user_info;

# COMMAND ----------

def create_volume(in_catalog: str, in_schema: str, volume_name: str):
    '''
    Create a volume in the specified catalog.schema.
    '''
    print(f'Creating volume: {in_catalog}.{in_schema}.{volume_name} if not exists.\n')
    r = spark.sql(f'CREATE VOLUME IF NOT EXISTS {in_catalog}.{in_schema}.{volume_name}')

# COMMAND ----------

# @DBAcademyHelper.add_method
# def create_catalogs(self, catalog_suffix: list):
def create_schemas(in_catalog: str, schema_names: list):
    '''
    Create schemas for the course in the specified catalog. Use DA.catalog_name in vocareum.

    If the schemas do not exist in the environment it will creates the schemas based the user's schema_name list.

    Parameters:
    - schema_names (list): A list of strings representing schema names to creates.

    Returns:
        Log information:
            - If schemas(s) do not exist, prints information on the schemas it created.
            - If schemas(s) exist, prints information that schemas exist.

    Example:
    -------
    - create_schemas(in_catalog = DA.catalog_name, schema_names = ['1_bronze', '2_silver', '3_gold'])
    '''

    ## Current schemas in catalog
    list_of_curr_schemas = spark.sql(f'SHOW SCHEMAS IN {in_catalog}').toPandas().databaseName.to_list()

    # Create schema in catalog if not exists
    for schema in schema_names:
        if schema not in list_of_curr_schemas:
            print(f'Creating schema: {in_catalog}.{schema}.')
            spark.sql(f'CREATE SCHEMA IF NOT EXISTS {in_catalog}.{schema}')
        else:
            print(f'Schema {in_catalog}.{schema} already exists. No action taken.')

# COMMAND ----------

def check_if_schemas_are_created(in_catalog: str, check_schemas: list[str]):
    '''
    Search for the specified catalogs by looking at the last word separated by the _. Return error if those don't exist.

    Parameters:
    - in_catalog: Catalog to check for schemas
    - check_schemas: List of schemas to check for in the catalog above
        
    Returns:
    - Raises an error if the catalogs don't exists. Otherwise prints a successful note.

    Example:
    - check_if_schemas_are_created(in_catalog='mycatalog', check_schemas=['bronze', 'silver', 'gold'])
    '''

    ## Current schemas in catalog
    list_of_curr_schemas = set(spark.sql(f'SHOW SCHEMAS IN {in_catalog}').toPandas().databaseName.to_list())

    # Convert check_catalogs list to a set
    check_schemas_set = set(check_schemas)
    
    # Check if all items are in the predefined items set
    missing_items = check_schemas_set - list_of_curr_schemas
    
    if missing_items:
        # If there are any missing items, raise an error
        raise ValueError(f"The necessary schemas in your labuser schema ({check_schemas_set}) do not exist in your workspace. Please run the 0 - REQUIRED - Course Setup and Exploration notebook to setup your environment for this course.")
    
    # If all items are found, return True
    print(f'Schemas are available, lab check passed: {sorted(check_schemas_set)}.')


# check_if_schemas_are_created(in_catalog=DA.catalog_name, check_schemas=[DA.schema_bronze, DA.schema_silver, DA.schema_gold])

# COMMAND ----------

def delete_source_files(source_files: str):
    """
    Deletes all files in the specified source volume.

    This function iterates through all the files in the given volume,
    deletes them, and prints the name of each file being deleted.

    Parameters:
    - source_files : str
        The path to the volume containing the files to delete. 
        Use the {DA.paths.working_dir} to dynamically navigate to the user's volume location in dbacademy/ops/vocareumlab@name:
            Example: DA.paths.working_dir = /Volumes/dbacademy/ops/vocareumlab@name

    Returns:
    - None. This function does not return any value. It performs file deletion and prints all files that it deletes. If no files are found it prints in the output.

    Example:
    - delete_source_files(f'{DA.paths.working_dir}/pii/stream_source/user_reg')
    """

    import os

    print(f'\nSearching for files in {source_files} volume to delete prior to creating files...')
    if os.path.exists(source_files):
        list_of_files = sorted(os.listdir(source_files))
    else:
        list_of_files = None

    if not list_of_files:  # Checks if the list is empty.
        print(f"No files found in {source_files}.\n")
    else:
        for file in list_of_files:
            file_to_delete = source_files + file
            print(f'Deleting file: {file_to_delete}')
            dbutils.fs.rm(file_to_delete)

# COMMAND ----------

def copy_files(copy_from: str, copy_to: str, n: int, sleep=2):
    '''
    Copy files from one location to another destination's volume.

    This method performs the following tasks:
      1. Lists files in the source directory and sorts them. Sorted to keep them in the same order when copying for consistency.
      2. Verifies that the source directory has at least `n` files.
      3. Copies files from the source to the destination, skipping files already present at the destination.
      4. Pauses for `sleep` seconds after copying each file.
      5. Stops after copying `n` files or if all files are processed.
      6. Will print information on the files copied.
    
    Parameters
    - copy_from (str): The source directory where files are to be copied from.
    - copy_to (str): The destination directory where files will be copied to.
    - n (int): The number of files to copy from the source. If n is larger than total files, an error is returned.
    - sleep (int, optional): The number of seconds to pause after copying each file. Default is 2 seconds.

    Returns:
    - None: Prints information to the log on what files it's loading. If the file exists, it skips that file.

    Example:
    - copy_files(copy_from='/Volumes/gym_data/v01/user-reg', 
           copy_to=f'{DA.paths.working_dir}/pii/stream_source/user_reg',
           n=1)
    '''
    import os
    import time

    print(f"\n----------------Loading files to user's volume: '{copy_to}'----------------")

    ## List all files in the copy_from volume and sort the list
    list_of_files_to_copy = sorted(os.listdir(copy_from))
    total_files_in_copy_location = len(list_of_files_to_copy)

    ## Get a list of files in the source
    list_of_files_in_source = os.listdir(copy_to)

    assert total_files_in_copy_location >= n, f"The source location contains only {total_files_in_copy_location} files, but you specified {n}  files to copy. Please specify a number less than or equal to the total number of files available."

    ## Looping counter
    counter = 1

    ## Load files if not found in the co
    for file in list_of_files_to_copy:

      ## If the file is found in the source, skip it with a note. Otherwise, copy file.
      if file in list_of_files_in_source:
        print(f'File number {counter} - {file} is already in the source volume "{copy_to}". Skipping file.')
      else:
        file_to_copy = f'{copy_from}/{file}'
        copy_file_to = f'{copy_to}/{file}'
        print(f'File number {counter} - Copying file {file_to_copy} --> {copy_file_to}.')
        dbutils.fs.cp(file_to_copy, copy_file_to , recurse = True)
        
        ## Sleep after load
        time.sleep(sleep) 

      ## Stop after n number of loops based on argument.
      if counter == n:
        break
      else:
        counter = counter + 1

# COMMAND ----------

def copy_file_for_multiple_sources(copy_n_files = 2, 
                                   sleep_set = 3,
                                   copy_from_source=str,
                                   copy_to_target=str
                                   ):

    for n in range(copy_n_files):
        n = n + 1
        copy_files(copy_from = f'{copy_from_source}/orders/stream_json', copy_to = f'{copy_to_target}/orders', n = n, sleep=sleep_set)
        copy_files(copy_from = f'{copy_from_source}/customers/stream_json', copy_to = f'{copy_to_target}/customers', n = n, sleep=sleep_set)
        copy_files(copy_from = f'{copy_from_source}/status/stream_json', copy_to = f'{copy_to_target}/status', n = n, sleep=sleep_set)

# COMMAND ----------

import os
def create_directory_in_user_volume(user_default_volume_path: str, create_folders: list):
    '''
    Creates multiple (or single) directories in the specified volume path.

    Parameters:
    - user_default_volume_path (str): The base directory path where the folders will be created. 
                                      You can use the default DA.paths.working_dir as the user's volume path.
    - create_folders (list): A list of strings representing folder names to be created within the base directory.

    Returns:
    - None: This function does not return any values but prints log information about the created directories.

    Example: 
    - create_directory_in_user_volume(user_default_volume_path=DA.paths.working_dir, create_folders=['customers', 'orders', 'status'])
    '''
    
    print('----------------------------------------------------------------------------------------')
    for folder in create_folders:

        create_folder = f'{user_default_volume_path}/{folder}'

        if not os.path.exists(create_folder):
        # If it doesn't exist, create the directory
            dbutils.fs.mkdirs(create_folder)
            print(f'Creating folder: {create_folder}')

        else:
            print(f"Directory {create_folder} already exists. No action taken.")
        
    print('----------------------------------------------------------------------------------------\n')

# COMMAND ----------

def display_config_values(config_values):
    """
    Displays list of key-value pairs as rows of HTML text and textboxes
    
    Parameters:
    - config_values: list of (key, value) tuples
        
    Returns:
    - HTML output displaying the config values

    Example:
    - DA.display_config_values([('catalog',DA.catalog_name),('schema',DA.schema_name)])
    """
    html = """<table style="width:100%">"""
    for name, value in config_values:
        html += f"""
        <tr>
            <td style="white-space:nowrap; width:1em">{name}:</td>
            <td><input type="text" value="{value}" style="width: 100%"></td></tr>"""
    html += "</table>"
    displayHTML(html)

# COMMAND ----------

def drop_tables(in_catalog: str, in_schema: list, dry_run: bool = False) -> list:
    """
    Drops all tables and views in the specified schema within a given catalog.

    Args:
        in_catalog (str): The catalog name (e.g., 'dbacademy_peter').
        in_schema (str): The schema name (e.g., 'default').
        dry_run (bool): If True, only prints tables that would be dropped without actually dropping them.

    Returns:
        list: Fully qualified names of the tables that were dropped (or would be dropped in dry-run mode).

    Example:
    >>> drop_tables(in_catalog='dbacademy_peter', in_schema='1_bronze_db')
    """
    # Check if catalog exists
    catalogs = [row.catalog for row in spark.sql("SHOW CATALOGS").collect()]
    if in_catalog not in catalogs:
        raise ValueError(f"Catalog '{in_catalog}' does not exist.")

    ## Delete tables and views in schema
    for schema in in_schema:
        
        # Check if schema exists in the catalog
        full_schema = f"{in_catalog}.{schema}"
        if not spark.catalog.databaseExists(full_schema):
            raise ValueError(f"Schema '{schema}' does not exist in catalog '{in_catalog}'.")
        
        print(f"\n{'Previewing' if dry_run else 'Dropping'} all tables in {in_catalog}.{schema}:")

        # Get all tables in the schema
        tables = spark.sql(f"SHOW TABLES IN {in_catalog}.{schema}").collect()

        if not tables:
            print(f"No tables found in schema {in_catalog}.{schema}. Nothing to drop.")
        else:
            table_names = [f"{in_catalog}.{schema}.{t.tableName}" for t in tables]

            for table_full_name in table_names:
                if dry_run:
                    print(f"Would drop: {table_full_name}")
                else:
                    try:
                        spark.sql(f"DROP TABLE IF EXISTS {table_full_name}")
                        print(f"Dropped TABLE: {table_full_name}")
                    except:
                        spark.sql(f"DROP VIEW IF EXISTS {table_full_name}")
                        print(f"Dropped VIEW: {table_full_name}")

# COMMAND ----------

import json
import os
import json
from databricks.sdk import WorkspaceClient


def create_declarative_pipeline(pipeline_name: str, 
                        root_path_folder_name: str,
                        source_folder_names: list = [],
                        catalog_name: str = 'dbacademy',
                        schema_name: str = 'default',
                        serverless: bool = True,
                        configuration: dict = {},
                        continuous: bool = False,
                        photon: bool = True,
                        channel: str = 'PREVIEW',
                        development: bool = True,
                        pipeline_type = 'WORKSPACE'
                        ):
  
    '''
  Creates the specified DLT pipeline.

  Parameters:
  ----------
  pipeline_name : str
      The name of the DLT pipeline to be created.
  root_path_folder_name : str
      The root folder name where the pipeline will be located. This folder must be in the location where this function is called.
  source_folder_names : list, optional
      A list of source folder names. Must defined at least one folder within the root folder location above.
  catalog_name : str, optional
      The catalog name for the DLT pipeline. Default is 'dbacademy'.
  schema_name : str, optional
      The schema name for the DLT pipeline. Default is 'default'.
  serverless : bool, optional
      If True, the pipeline will be serverless. Default is True.
  configuration : dict, optional
      A dictionary of configuration settings for the pipeline. Default is an empty dictionary.
  continuous : bool, optional
      If True, the pipeline will be run in continuous mode. Default is False.
  photon : bool, optional
      If True, the pipeline will use Photon for processing. Default is True.
  channel : str, optional
      The channel for the pipeline, such as 'PREVIEW'. Default is 'PREVIEW'.
  development : bool, optional
      If True, the pipeline will be set up for development. Default is True.
  pipeline_type : str, optional
      The type of the pipeline (e.g., 'WORKSPACE'). Default is 'WORKSPACE'.

  Returns:
  -------
  None
      This function does not return anything. It creates the DLT pipeline based on the provided parameters.

  Example:
  --------
  create_dlt_pipeline(pipeline_name='my_pipeline_name', 
                      root_path_folder_name='6 - Putting a DLT Pipeline in Production Project',
                      source_folder_names=['orders', 'status'])
  '''
  
    w = WorkspaceClient()
    for pipeline in w.pipelines.list_pipelines():
        if pipeline.name == pipeline_name:
            raise ValueError(f"Lakeflow Declarative Pipeline name '{pipeline_name}' already exists. Please delete the pipeline using the UI and rerun the cell to recreate the pipeline.")

    ## Create empty dictionary
    create_dlt_pipeline_call = {}

    ## Pipeline type
    create_dlt_pipeline_call['pipeline_type'] = pipeline_type

    ## Modify dictionary for specific DLT configurations
    create_dlt_pipeline_call['name'] = pipeline_name

    ## Set paths to root and source folders
    main_course_folder_path = os.getcwd()

    main_path_to_dlt_project_folder = os.path.join('/', main_course_folder_path, root_path_folder_name)
    create_dlt_pipeline_call['root_path'] = main_path_to_dlt_project_folder

    ## Add path of root folder to source folder names
    add_path_to_folder_names = [os.path.join(main_path_to_dlt_project_folder, folder_name, '**') for folder_name in source_folder_names]
    source_folders_path = [{'glob':{'include':folder_name}} for folder_name in add_path_to_folder_names]
    create_dlt_pipeline_call['libraries'] = source_folders_path

    ## Set default catalog and schema
    create_dlt_pipeline_call['catalog'] = catalog_name
    create_dlt_pipeline_call['schema'] = schema_name

    ## Set serverless compute
    create_dlt_pipeline_call['serverless'] = serverless

    ## Set configuration parameters
    create_dlt_pipeline_call['configuration'] = configuration

    ## Set if continouous or not
    create_dlt_pipeline_call['continuous'] = continuous 

    ## Set to use Photon
    create_dlt_pipeline_call['photon'] = photon

    ## Set DLT channel
    create_dlt_pipeline_call['channel'] = channel

    ## Set if development mode
    create_dlt_pipeline_call['development'] = development

    ## Creat DLT pipeline

    print(f"Creating the Lakeflow Declarative Pipeline '{pipeline_name}'...")
    print(f"Root folder path: {main_path_to_dlt_project_folder}")
    print(f"Source folder path(s): {source_folders_path}")

    w.api_client.do('POST', '/api/2.0/pipelines', body=create_dlt_pipeline_call)
    print(f"\nLakeflow Declarative Pipeline Creation '{pipeline_name}' Complete!")

# COMMAND ----------

def setup_complete():
  '''
  Prints a note in the output that the setup was complete.
  '''
  print('\n\n\n------------------------------------------------------------------------------')
  print('SETUP COMPLETE!')
  print('------------------------------------------------------------------------------')

# COMMAND ----------

# @DBAcademyHelper.add_method
# def create_DA_keys(self): 
#     '''
#     Create the DA references to the bronze, silver and gold catalogs for the user.
#     '''
#     print('Set DA dynamic references to the dev, stage and prod catalogs.\n')
#     setattr(DA, f'catalog_bronze', f'{self.catalog_name}_bronze_1')
#     setattr(DA, f'catalog_silver', f'{self.catalog_name}_silver_2')
#     setattr(DA, f'catalog_gold', f'{self.catalog_name}_gold_3')