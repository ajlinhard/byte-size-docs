-- Databricks notebook source
-- MAGIC %run ../../Includes/Classroom-Setup-2

-- COMMAND ----------

USE CATALOG IDENTIFIER(DA.catalog_name);

-- COMMAND ----------

SELECT *
FROM 1_bronze_db.orders_bronze
LIMIT 10;

-- COMMAND ----------

SELECT *
FROM 2_silver_db.orders_silver
LIMIT 10;

-- COMMAND ----------

SELECT *
FROM 3_gold_db.gold_orders_by_date