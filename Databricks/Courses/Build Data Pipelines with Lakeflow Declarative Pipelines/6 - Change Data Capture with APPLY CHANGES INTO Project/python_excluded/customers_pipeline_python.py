# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # More DLT Python Syntax
# MAGIC
# MAGIC DLT Pipelines make it easy to combine multiple datasets into a single scalable workload using one or many notebooks.
# MAGIC
# MAGIC In the last notebook, we reviewed some of the basic functionalities of DLT syntax while processing data from cloud object storage through a series of queries to validate and enrich records at each step. This notebook similarly follows the medallion architecture, but introduces a number of new concepts.
# MAGIC * Raw records represent change data capture (CDC) information about customers 
# MAGIC * The bronze table again uses Auto Loader to ingest JSON data from cloud object storage
# MAGIC * A table is defined to enforce constraints before passing records to the silver layer
# MAGIC * **`dlt.apply_changes()`** is used to automatically process CDC data into the silver layer as a Type 2 <a href="https://en.wikipedia.org/wiki/Slowly_changing_dimension" target="_blank">slowly changing dimension (SCD) table</a>
# MAGIC * A gold table is defined to calculate an aggregate from the current version of this Type 1 table
# MAGIC * A view is defined that joins with tables defined in another notebook
# MAGIC
# MAGIC ## Learning Objectives
# MAGIC
# MAGIC By the end of this lesson, students should feel comfortable:
# MAGIC * Processing CDC data with **`dlt.apply_changes()`**
# MAGIC * Declaring live views
# MAGIC * Joining live tables
# MAGIC * Describing how DLT library notebooks work together in a pipeline
# MAGIC * Scheduling multiple notebooks in a DLT pipeline

# COMMAND ----------

import dlt
import pyspark.sql.functions as F

source = spark.conf.get("source")

# COMMAND ----------

# MAGIC %md
# MAGIC ## A. Ingest Data with Auto Loader
# MAGIC
# MAGIC As in the last notebook, we define a bronze table against a data source configured with Auto Loader.
# MAGIC
# MAGIC Note that the code below omits the Auto Loader option to infer schema. When data is ingested from JSON without the schema provided or inferred, fields will have the correct names but will all be stored as **`STRING`** type.
# MAGIC
# MAGIC #### Specifying Table Names
# MAGIC
# MAGIC The code below demonstrates the use of the **`name`** option for DLT table declaration. The option allows developers to specify the name for the resultant table separate from the function definition that creates the DataFrame the table is defined from.

# COMMAND ----------

## A. Ingest Data with Auto Loader
@dlt.table(
    name="1_bronze_db.customers_bronze_raw_demo6",
    comment="Raw data from customers CDC feed",
    table_properties={
        "quality": "bronze"
    }
)
def customers_bronze_raw_demo6():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load(f"{source}/customers")
        .select(
            "*",
            F.current_timestamp().alias("processing_time"), 
            "_metadata.file_name"
        )
        .withColumnRenamed("file_name", "source_file")
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## B. Quality Enforcement Continued
# MAGIC
# MAGIC The query below demonstrates:
# MAGIC * The 3 options for behavior when constraints are violated
# MAGIC * A query with multiple constraints
# MAGIC * Multiple conditions provided to one constraint
# MAGIC * Using a built-in SQL function in a constraint
# MAGIC
# MAGIC About the data source:
# MAGIC * Data is a CDC feed that contains **`INSERT`**, **`UPDATE`**, and **`DELETE`** operations. 
# MAGIC * Update and insert operations should contain valid entries for all fields.
# MAGIC * Delete operations should contain **`NULL`** values for all fields other than the timestamp, **`customer_id`**, and operation fields.
# MAGIC
# MAGIC In order to ensure only good data makes it into our silver table, we'll write a series of quality enforcement rules that ignore the expected null values in delete operations.
# MAGIC
# MAGIC We'll break down each of these constraints below:
# MAGIC
# MAGIC ##### **`valid_id`**
# MAGIC This constraint will cause our transaction to fail if a record contains a null value in the **`customer_id`** field.
# MAGIC
# MAGIC ##### **`valid_operation`**
# MAGIC This constraint will drop any records that contain a null value in the **`operation`** field.
# MAGIC
# MAGIC ##### **`valid_address`**
# MAGIC This constraint checks if the **`operation`** field is **`DELETE`**; if not, it checks for null values in any of the 4 fields comprising an address. Because there is no additional instruction for what to do with invalid records, violating rows will be recorded in metrics but not dropped.
# MAGIC
# MAGIC ##### **`valid_email`**
# MAGIC This constraint uses regex pattern matching to check that the value in the **`email`** field is a valid email address. It contains logic to not apply this to records if the **`operation`** field is **`DELETE`** (because these will have a null value for the **`email`** field). Violating records are dropped.

# COMMAND ----------

## B. Quality Enforcement Silver
@dlt.table(
    name="1_bronze_db.customers_bronze_clean_demo6",
    comment="Raw data from customers CDC feed",
    table_properties={
        "quality": "bronze",
    }
)
@dlt.expect_or_fail("valid_id", "customer_id IS NOT NULL")
@dlt.expect_or_drop("valid_operation", "operation IS NOT NULL")
@dlt.expect("valid_name", "name IS NOT NULL or operation = 'DELETE'")
@dlt.expect("valid_adress", """
    (address IS NOT NULL and 
    city IS NOT NULL and 
    state IS NOT NULL and 
    zip_code IS NOT NULL) or
    operation = "DELETE"
    """)
@dlt.expect_or_drop("valid_email", """
    rlike(email, '^([a-zA-Z0-9_\\\\-\\\\.]+)@([a-zA-Z0-9_\\\\-\\\\.]+)\\\\.([a-zA-Z]{2,5})$') or 
    operation = "DELETE"
    """)
def customers_bronze_clean_demo6():
    return (
        dlt
        .read_stream("1_bronze_db.customers_bronze_raw_demo6")
        .select(
            "*",
            F.from_unixtime(F.col("timestamp")).cast("timestamp").alias("timestamp_datetime")
        )
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Processing CDC Data with **`dlt.apply_changes()`**
# MAGIC
# MAGIC DLT introduces a new syntactic structure for simplifying CDC feed processing.
# MAGIC
# MAGIC **`dlt.apply_changes()`** has the following guarantees and requirements:
# MAGIC * Performs incremental/streaming ingestion of CDC data
# MAGIC * Provides simple syntax to specify one or many fields as the primary key for a table
# MAGIC * Default assumption is that rows will contain inserts and updates
# MAGIC * Can optionally apply deletes
# MAGIC * Automatically orders late-arriving records using user-provided sequencing field
# MAGIC * Uses a simple syntax for specifying columns to ignore with the **`except_column_list`**
# MAGIC * Will default to applying changes as Type 2 SCD.

# COMMAND ----------

dlt.create_streaming_table(
    name = "2_silver_db.customers_silver_demo6",
    comment = 'SCD Type 2 Historical Customer Data')


dlt.apply_changes(
    target = "2_silver_db.customers_silver_demo6",
    source = "1_bronze_db.customers_bronze_clean_demo6",
    keys = ["customer_id"],
    sequence_by = "timestamp_datetime",
    apply_as_deletes = F.expr("operation = 'DELETE'"),
    except_column_list = ["operation", "timestamp", "_rescued_data"],
    stored_as_scd_type = 2
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## D. Querying Tables with Applied Changes
# MAGIC Create a materialized view that contains all current customers by filtering for `null` values in the **__END_AT** column.

# COMMAND ----------

@dlt.table(
    name="3_gold_db.current_customers_gold_demo6",
    comment="Current updated list of active customers"
)
def create_current_customers_gold_demo6():
    df = (dlt
          .read("2_silver_db.customers_silver_demo6") 
          .filter("__END_AT IS NULL") 
          .drop("processing_time") 
          .withColumn("updated_at", F.current_timestamp())
        )
    return df

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>