# Delta Live Tables (DLT) Overview
DLT is a syntax to help with a data pipelines using a declarative instead of an imperative definition of data pipelines. This is a response to the reality of the medallion architecture in the real-world of data engineer in the image below.

**NOTE:** Some of the information below is from this [Databricks Academy Resource](https://customer-academy.databricks.com/learn/courses/2971/build-data-pipelines-with-lakeflow-declarative-pipelines/lessons/32807/introduction-to-delta-live-tables)

### Table of Contents

- [Large scale ETL is complex and brittle](#large-scale-etl-is-complex-and-brittle)
  - [Complex pipeline development](#complex-pipeline-development)
  - [Data quality and governance](#data-quality-and-governance)
  - [Difficult pipeline operations](#difficult-pipeline-operations)
- [Materialized Views](#materialized-views)
- [Streaming Table](#streaming-table)
  - [Functionality](#functionality)
- [Steps To Create DLT Pipeline](#steps-to-create-dlt-pipeline)
  - [Development vs Production Mode](#development-vs-production-mode)
  - [Dependencies](#dependencies)
  - [Expections](#expections)
- [Pipeline UI](#pipeline-ui)
- [Parameterize Pipelines](#parameterize-pipelines)
- [DLT Correct Usage and Limitations](#dlt-correct-usage-and-limitations)
- [Schema Evolution Support in DLT](#schema-evolution-support-in-dlt)
  - [Automatic Schema Evolution Support](#automatic-schema-evolution-support)
  - [Materialized Views](#materialized-views-1)
  - [Streaming Tables](#streaming-tables)
  - [Key Limitations and Workarounds](#key-limitations-and-workarounds)
  - [Best Practices](#best-practices)

![image](https://github.com/user-attachments/assets/384ac50b-38e4-41f7-9cd3-4e655ef00482)

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
```

## Steps To Create DLT Pipeline
![image](https://github.com/user-attachments/assets/1747077e-ccf6-4c62-b49f-f465e392b88c)

### Development vs Production Mode
The difference between development mode and production mode has to do with the nature of how you will want to iterate fast while developing vs. efficency and reliability in production.

**Development**
- resuse a long-running cluster for quick reruns as you adjust and fix queries.
- No retries on errors enabling the error to appear sooner. Retries are auto attempts to process data through in the pipeline

### Dependencies
No matter how many notebooks you include in your DLT the DLT system will wire the correct query order together.

**Features**
- parallelsim is automatic if 2+ tables have all dependencies satisfied.
- LIVE dependencies from the same pipeline, are read from the LIVE schema
- Other producers are just read from the catalog or spark data source as they normally would.

### Expections
These are test that ensure the data quality. They are true/false expressions that are used to validate each row during processing. They are basically, constraints on steriods. DLT offers flexible policies on how to process record that violate the expectation:
- Track number of bad records
- Drop bad records
- Abort processing for a single bad record
- Link to more [Databricks Expectations Info](https://docs.databricks.com/aws/en/dlt/expectations)

```sql
CONSTRAINT valid_ts EXPECT (ts > '2012-01-01')
ON VIOLATION DROP
```
```python
@dlt.expect_or_drop("valid_ts", col("ts") > '2012-01-01')
```

## Pipeline UI
The DLT tables had a live you I for visulizing and watching the data flow through the system.
Additionally:
- Table/View Level Insights
  - Look at the expectations on each table.
  - Check the quailty and use of those expectations for the latest run.
  - Look at data columns in the table
- Access Historical updates
  - Look at all past runs with the same features listed above.
- Control Operations
  - Put the DLT table into and out of production
  - Add permission to the pipeline
  - Schedule the pipeline to be continuous or every X amount of time
  - Full Refresh All option: force all the original files to be re-processed again.
    - Useful during development if you make a change.
    - Can result in a lost of data, transactional info. etc.
- Audit Log
  - Allows you to deep dive into events that occurred within your data.
  - Export them to another table for investigation and additional stats of feeds.
 
## Parameterize Pipelines
To avoid hard coding paths, catalogs, schmea, etc you may want to parameterize the pipeline for ease reuse.

---
# DLT Correct Usage and Limitations
Databricks Delta Live Tables (DLT) has several limitations and scenarios where it may not be the best choice:

**Real-time streaming limitations:**
- DLT is optimized for micro-batch processing rather than true real-time streaming
- Not ideal for applications requiring sub-second latency
- Limited support for complex event processing patterns

**Cost considerations:**
- Can be expensive for simple ETL workloads that don't require the full feature set
- Compute costs can add up quickly for continuously running pipelines
- May be overkill for basic data transformation needs

**Flexibility constraints:**
- More opinionated than custom Spark jobs, which can limit certain advanced use cases
- Predefined pipeline structure may not fit all data processing patterns
- Limited ability to integrate with non-Databricks systems directly

**Operational limitations:**
- Debugging can be more challenging compared to traditional Spark applications
- Less granular control over resource allocation and optimization
- Pipeline dependency management can become complex in large environments

**Technical constraints:**
- Not suitable for workloads requiring custom libraries or specialized frameworks
- Limited support for certain data formats or sources
- May struggle with very large-scale batch processing that requires fine-tuned optimization

**Use case mismatches:**
- Ad-hoc data analysis or exploratory data science work
- Simple scheduled batch jobs that don't need pipeline orchestration
- Applications requiring tight integration with external systems or APIs
- Workloads that need to run outside the Databricks ecosystem

DLT works best for medallion architecture implementations, data quality enforcement, and managed ETL/ELT pipelines, but it's not a universal solution for all data processing needs.

## Schema Evolution Support in DLT

**Yes**, DLT does allow schema evolution for both materialized views and streaming tables, **BUT** with important limitations and considerations:

### Automatic Schema Evolution Support

DLT automatically handles adding new columns to streaming tables. The following data type changes are handled automatically: changing from NullType to any other type, and upcasts from ByteType → ShortType → IntegerType.

For incompatible schema changes in streaming tables, data is rescued into the _rescued_data column rather than causing pipeline failures.

### Materialized Views
For materialized views to support incremental refresh, source data should be stored in Delta tables with row tracking and change data feed enabled. When schema changes occur in the underlying tables, materialized views can be refreshed to accommodate the changes, though when materialized views are created over source tables that contain row filters and column masks, the refresh is always a full refresh.

### Streaming Tables
In DLT streaming pipelines, adding new columns is automatically handled. However, when there are incompatible data type changes for existing columns, the pipeline will rescue the incompatible data to the _rescued_data column.

### Key Limitations and Workarounds

**Data Type Changes:** When incompatible schema changes occur, you may need to perform a full refresh of the pipeline or create additional versioned tables and union them with views.

**Column Renaming:** Column renaming is not automatically supported for streaming tables in Unity Catalog. You can handle this by coalescing the old and new columns in your transformations.

**Configuration:** You can enable automatic schema merging using spark.databricks.delta.schema.autoMerge.enabled configuration for streaming data.

### Best Practices
- Design schemas to anticipate future changes
- Use the `mergeSchema` option when writing to Delta tables
- Monitor pipeline behavior to verify incremental vs. full refreshes
- Consider using versioned tables for major schema changes

While DLT provides good support for additive schema changes (new columns), non-additive changes (column renames, type changes) require more careful handling and may necessitate full refreshes or manual intervention.
