# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
# MAGIC </div>
# MAGIC

# COMMAND ----------

## The below code produces an error when run in a standalone notebook and not as part of a job because job/task parameters are not sent into a standalone notebook without the job. You can set a default widgets  with the following code to run standalone

# dbutils.widgets.text(name='catalog', defaultValue='dbacademy')
# dbutils.widgets.text(name='schema', defaultValue='your-lab-user-name')

# COMMAND ----------

## Store the values from the text input widgets into variables
my_catalog = dbutils.widgets.get('catalog')
my_schema = dbutils.widgets.get('schema')


## Set path to your volume
my_volume_path = f"/Volumes/{my_catalog}/{my_schema}/trigger_storage_location/"


## Display the variables
print(my_catalog)
print(my_schema)
print(my_volume_path)

# COMMAND ----------



## Load the babynames.csv file from the volume
babynames = (spark
             .read
             .format("csv")
             .option("header", "true")
             .option("inferSchema", "true")
             .load(f'{my_volume_path}babynames.csv')
)

## Display 2014 names
display(babynames.filter(babynames.Year == "2014"))

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>