# Databricks notebook source
# MAGIC %run ./Classroom-Setup-Common

# COMMAND ----------

## Create catalogs for the course
create_schemas(in_catalog = DA.catalog_name, schema_names = ['1_bronze_db', '2_silver_db', '3_gold_db'])


## Create directories in the specified volume
create_directory_in_user_volume(user_default_volume_path = DA.paths.working_dir, create_folders = ['customers', 'orders', 'status'])


## Delete all files in the labuser's volume to reset the class if necessary. Otherwise does nothing.
delete_source_files(f'{DA.paths.working_dir}/customers/')
delete_source_files(f'{DA.paths.working_dir}/orders/')
delete_source_files(f'{DA.paths.working_dir}/status/')


##
## Start each directory in the labuser's volume with one file.
##

## Customers
copy_files(copy_from='/Volumes/dbacademy_retail/v01/retail-pipeline/customers/stream_json', 
           copy_to=f'{DA.paths.working_dir}/customers', 
           n=1)

## Orders
copy_files(copy_from='/Volumes/dbacademy_retail/v01/retail-pipeline/orders/stream_json', 
           copy_to=f'{DA.paths.working_dir}/orders', 
           n=1)

## Customers
copy_files(copy_from='/Volumes/dbacademy_retail/v01/retail-pipeline/status/stream_json', 
           copy_to=f'{DA.paths.working_dir}/status', 
           n=1)



setup_complete()