# Databricks notebook source
# MAGIC %run ./Classroom-Setup-Common

# COMMAND ----------

# MAGIC %run ../Includes/Classroom-Setup-1-setup-REQUIRED

# COMMAND ----------

## Check to see if schemas for the user are ready. If they are not, an error is returned.
check_if_schemas_are_created(in_catalog=DA.catalog_name, check_schemas=['1_bronze_db', '2_silver_db', '3_gold_db'])

## Display the course catalog and schema name for the user.
display_config_values(
  [
    ('Your catalog name variable reference: DA.catalog_name', DA.catalog_name),
    ('Variable reference to your source files (Python - DA.paths.working_dir, SQL - DA.paths_working_dir)', DA.paths.working_dir)
   ]
)