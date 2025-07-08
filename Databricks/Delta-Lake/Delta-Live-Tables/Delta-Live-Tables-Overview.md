# Delta Live Tables (DLT) Overview
DLT is a syntax to help with a data pipelines using a declarative instead of an imperative definition of data pipelines. This is a response to the reality of the medallion architecture in the real-world of data engineer in the image below.

![image](https://github.com/user-attachments/assets/dee71ff8-c1ec-4e4e-a633-59788742ca36)

## Large scale ETL is complex and brittle
The reality is the downhill flow of data cascades in a non-linear fashions creating dependencies of the freshness of data from many fields and feeds.

### Complex pipeline development
- Hard to build and maintain table **dependencies**
- Difficult to switch between **batch** and **stream** processing

### Data quality and governance
- Difficult to monitor and enforce **data quality**
- Impossible to trace data **lineage**

### Difficult pipeline operations
- Poor **observability** at granular, data level
- Error handling and **recovery** is laborious


## Materialized Views
A meterialized view is a query which stores the information from its previous runs in order to decrease the runtime of future runs and increase efficiency.
- defined by a SQL query
- Created and kept up-to-date by a pipeline
Notes:
- Its recommended most gold layers are materialized views
- the "LIVE.{table name}" syntax is required.

```sql
CREATE OR REFRESH MATERIALIZED VIEW report
as
SELECT country, sum(profit)
FROM LIVE.sales
GROUP BY country
```

## Streaming Table
Streaming tables can come from many data sources:
- Stream sources like Kafka, AWS Kinesis, etc
- Auto-loader (Databricks)
- Other Streaming Tables

#### Functionality
- Append-Only, so data can only be added to the stream, not updated.
- Any append-only delta table can be read as a stream, whether from a live schema, the unity catalog, or a folder path.
  - This means streaming tables CANNOT:
  - be the target of APPLY CHANGES INTO
  - define aggregate function
  - be a tables which you've executed DML to delete/update
- The streaming tables are Stateful, meaning the previous runs of the tables are known and stored.

```sql
CREATE STREAMING TABLE mystream
AS SELECT *
FROM STREAM(LIVE.my_table)
