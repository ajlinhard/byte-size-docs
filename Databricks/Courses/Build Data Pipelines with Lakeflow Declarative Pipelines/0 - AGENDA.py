# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Build Data Pipeline with Lakeflow Declarative Pipelines
# MAGIC
# MAGIC ---
# MAGIC ### Course Agenda
# MAGIC The following modules are part of the **Data Engineer Learning** Path by Databricks Academy.
# MAGIC | # | Notebook Name |
# MAGIC | --- | --- |
# MAGIC | 1 | [REQUIRED - Course Setup and Creating a Pipeline]($./1 - REQUIRED - Course Setup and Creating a Pipeline) |
# MAGIC | 2 | [Developing a Simple Pipeline]($./2 - Developing a Simple Pipeline) |
# MAGIC | 3 | [Adding Data Quality Expectations]($./3 - Adding Data Quality Expectations) |
# MAGIC | 4L | [Create a Pipeline]($./4 Lab - Create a Pipeline) |
# MAGIC | 5 | [Deploying a Pipeline to Production]($./5 - Deploying a Pipeline to Production) |
# MAGIC | 6 | [Change Data Capture with APPLY CHANGES INTO]($./6 - Change Data Capture with APPLY CHANGES INTO) |
# MAGIC | 7L | [APPLY CHANGES INTO with SCD Type 1]($./7 BONUS Lab - APPLY CHANGES INTO with SCD Type 1) |
# MAGIC
# MAGIC --- 
# MAGIC
# MAGIC ### Requirements
# MAGIC
# MAGIC Please review the following requirements before starting the lesson:
# MAGIC
# MAGIC * To run demo and lab notebooks, you need to use the following Databricks runtime: **`16.4.x-scala2.12`**
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>