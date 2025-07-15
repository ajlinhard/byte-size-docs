# Lakeflow Connect Overview
Lakeflow and its supporting connectors are all about bringing data into Databricks. There are 3 buckets of options for this:
- Upload Files
- Standard Connectors
- Managed Connectors

## Summary of Options
![image](https://github.com/user-attachments/assets/cb142467-ee2f-472c-9546-a0acf1b131d3)


## Methods of Loading
Batch Processing
- Loading data as batches of rows into a system (Databricks), often based on a schedule.
- Traditional batch ingestion is processing all records each time
  - create tables as (CTAS)
  - spark.read.load()

Incremental Batch
- Only new data is ingested previously, loaded records are skipped automatically.
- Faster ingestion and better resource efficency by processing less data.
  - create or refresh streaming table
  - spark.readStream(AutoLoader with timed trigger)
  - DLT pipelines

Streaming
- Continuously load data rows or batches or data rows as it is generated so you can query it as it arrives in near real-time.
- Micro-batch processes small batches in a very short, frequent intervals
- spark.readStream(AutoLoader with continuous trigger)
- DLT (trigger mode contiuous)

## Lakeflow Relationship with ETL + Auto Loader + DLT
The high-level relationship is:

Auto Loader: The ingestion mechanism
DLT: The pipeline framework that orchestrates transformations (often starting with Auto Loader)
Lakeflow: The broader workflow orchestration platform

- **Auto Loader** = Narrow, specialized tool focused solely on incremental file ingestion from cloud storage into Databricks. It does one thing really well: detecting new files and streaming them into your lakehouse.
- **Delta Live Tables (DLT)** = Broader ETL/data pipeline framework that handles the entire data transformation workflow. DLT often *uses* Auto Loader as its ingestion component, but then orchestrates all the downstream transformations, data quality checks, and pipeline dependencies.
- **Lakeflow** = Even broader workflow orchestration platform that can handle data pipelines, ML workflows, business processes, and other complex multi-step workflows across your organization.

The typical flow would be:
1. **Auto Loader** → "New files detected, streaming them in"
2. **DLT** → "Taking that ingested data and transforming it through bronze/silver/gold layers with quality checks"
3. **Lakeflow** → "Orchestrating the entire end-to-end process, maybe triggering ML model retraining after data pipeline completes"

Auto Loader is essentially the "data ingestion engine" that plugs into these larger frameworks. It's laser-focused on solving the specific technical challenges of reliable, efficient file loading (schema evolution, file discovery, error handling, checkpointing, etc.) rather than trying to be a general-purpose pipeline or workflow tool.

This specialization is actually a strength - it means Auto Loader can be really good at file ingestion and can be used by multiple different orchestration frameworks, not just DLT.
