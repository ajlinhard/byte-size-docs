# Databricks notebook source
# MAGIC %run ./Classroom-Setup-Common

# COMMAND ----------

DA = DBAcademyHelper()
DA.init()

DA.display_config_values([('Course Catalog',DA.catalog_name),('Your Schema',DA.schema_name)])

# The location that the DLT databases should be written to????
# setattr(DA, 'paths.storage_location', f'{DA.paths.working_dir}/storage_location')