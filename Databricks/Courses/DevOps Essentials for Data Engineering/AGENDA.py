# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # DevOps Essentials for Data Engineering
# MAGIC
# MAGIC This course is intended for complete beginners to Python, providing the basics of programmatically interacting with data. The course begins with a basic introduction to programming expressions, variables, and data types. It then progresses into conditional and control statements, followed by an introduction to methods and functions. You will learn the basics of data structures, classes, and various string and utility functions. Lastly, you will gain experience using the Pandas library for data analysis and visualization, as well as the fundamentals of cloud computing. Throughout the course, you will gain hands-on practice through lab exercises, with additional resources to deepen your knowledge of programming after the class.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Prerequisites
# MAGIC You should meet the following prerequisites before starting this course:
# MAGIC
# MAGIC - Proficient knowledge of the Databricks platform, including experience with Databricks Workspaces, Apache Spark, Delta Lake and
# MAGIC the Medallion Architecture, Unity Catalog, Delta Live Tables, and Workflows. A basic understanding of Git version control is also
# MAGIC required.
# MAGIC - Experience ingesting and transforming data, with proficiency in PySpark for data processing and DataFrame manipulations.
# MAGIC Additionally, candidates should have experience writing intermediate level SQL queries for data analysis and transformation.
# MAGIC - Knowledge of Python programming, with proficiency in writing intermediate level Python code, including the ability to design and
# MAGIC implement functions and classes. Users should also be skilled in creating, importing, and effectively utilizing Python packages.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Course Agenda:
# MAGIC
# MAGIC The following modules are part of the **Data Engineer Learning** Path by Databricks Academy.
# MAGIC
# MAGIC  Module | Notebook Name |
# MAGIC |-------|-------------|
# MAGIC  **[M02 - CI]($./Course Notebooks/M02 - CI)**    |[2.1 - Modularizing PySpark Code - REQUIRED]($./Course Notebooks/M02 - CI/2.1 - Modularizing PySpark Code - REQUIRED)<br>[2.2L - Modularize PySpark Code]($./Course Notebooks/M02 - CI/2.2L - Modularize PySpark Code)<br>[2.3 - Project Setup Exploration]($./Course Notebooks/M02 - CI/2.3 - Project Setup Exploration)<br>[2.4 - Creating and Executing Unit Tests]($./Course Notebooks/M02 - CI/2.4 - Creating and Executing Unit Tests) <br>[2.5L - Create and Execute Unit Tests]($./Course Notebooks/M02 - CI/2.5L - Create and Execute Unit Tests)<br>[2.6 - Performing Integration Tests]($./Course Notebooks/M02 - CI/2.6 - Performing Integration Tests)<br>[2.7L - Version Control with Databricks Git Folders and GitHub]($./Course Notebooks/M02 - CI/2.7L - Version Control with Databricks Git Folders and GitHub)|
# MAGIC  **[M03 - CD]($./Course Notebooks/M03 - CD)** |[3.1 - Deploying the Databricks Assets]($./Course Notebooks/M03 - CD/3.1 - Deploying the Databricks Assets) | 
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Requirements
# MAGIC
# MAGIC Please review the following requirements before starting the lesson:
# MAGIC
# MAGIC * To run demo and lab notebooks, you need to use the following Databricks runtime: **`16.4.x-scala2.12`**
# MAGIC * This course will only run in the Databricks Academy labs.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>
# MAGIC