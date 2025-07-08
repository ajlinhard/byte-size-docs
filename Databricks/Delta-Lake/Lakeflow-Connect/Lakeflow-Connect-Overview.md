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
