# Databricks notebook source
# MAGIC %run ./Classroom-Setup-Lab

# COMMAND ----------

LabSetup.copy_file(copy_file = 'employees_1.csv', 
                   to_target_volume = f'/Volumes/{DA.catalog_name}/default/lab_files')


setup_complete()

## Display the course catalog and schema name for the user.
display_config_values(
  [
    ('Your catalog name variable reference: DA.catalog_name', DA.catalog_name),
    ('Your raw data source files',f'/Volumes/{DA.catalog_name}/default/lab_files')
   ]
)