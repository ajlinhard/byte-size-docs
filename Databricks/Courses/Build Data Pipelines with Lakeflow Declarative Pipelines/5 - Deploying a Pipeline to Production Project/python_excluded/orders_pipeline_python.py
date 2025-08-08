import dlt
import pyspark.sql.functions as F

source = spark.conf.get("source")


## A. Create the bronze streaming table in your labuser.1_bronze_db schema from a JSON files in your volume
  # NOTE: read_files references the 'source' configuration key from your DLT pipeline settings. 
  # NOTE: 'source' = '/Volumes/dbacademy/ops/your-labuser-name'
@dlt.table(name = "1_bronze_db.orders_bronze_demo5",
           comment = "Ingest order JSON files from cloud storage",
           table_properties = {
                            "quality":"bronze",
                            "pipelines.reset.allowed":"false"
                        })
def orders_bronze_demo5():
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.inferColumnTypes", True)
            .load(f"{source}/orders")
            .select(
                "*",
                F.current_timestamp().alias("processing_time"), 
                "_metadata.file_name"
            )
    )


## B. Create the silver streaming table in your labuser.2_silver_db schema (database)
@dlt.table(name = "2_silver_db.orders_silver_demo5",
           comment = "Silver clean orders table",
           table_properties = {
                            "quality":"silver"
                        })

# Expectations
@dlt.expect("valid_notifications", "notifications IN ('Y','N')")
@dlt.expect_or_drop("valid_date", F.col("order_timestamp") > "2021-12-25")
@dlt.expect_or_fail("valid_id", F.col("customer_id").isNotNull())

def orders_silver_demo5():
    return (
        dlt.read_stream("1_bronze_db.orders_bronze_demo5")
            .select(
                "order_id",
                F.col("order_timestamp").cast("timestamp").alias("order_timestamp"),
                "customer_id",
                "notifications"
            )
    )


## C. Create the materialized view aggregation from the orders_silver table with the summarization
@dlt.table(name = "3_gold_db.gold_orders_by_date_demo5",
           comment = "Aggregate gold data for downstream analysis",
           table_properties = {
                            "quality":"gold"
                        })
def gold_orders_by_date_demo5():
    return (
        dlt.read("2_silver_db.orders_silver_demo5")
            .groupBy(F.col("order_timestamp").cast("date").alias("order_date"))
            .agg(F.count("*").alias("total_daily_orders"))
    )