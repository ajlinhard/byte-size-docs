# Lakeflow Change Data Capture (CDC)
When upstream data is changing in a live OLTP system or ML/Window functions prepartion there may be a need to update downstream data accordingly. This is where the concept of CDC comes into play. Traditionally, this was done with the MERGE or MERGE INTO statement, but this can become complex if multiple changes are coming in for the same record ID. Thus with deduplication or other row reduction techniques CDC can become more lengthy. Also, the type of CDC you need can increase or decrease complex.

This is the reason for Databricks attempting to simplify the CDC with the APPLY CHANGED INTO command. With the goal of simplifying syntax and increasing performance.

### Documentation
- [Databricks - What is CDC?](https://docs.databricks.com/aws/en/dlt/what-is-change-data-capture)
- [Databricks - AUTO CDC API](https://docs.databricks.com/aws/en/dlt/cdc?language=Python)
- [Databricks - Delta Change Data Feeds (CDF)](https://docs.databricks.com/aws/en/delta/delta-change-data-feed)
- [Databricks - Old Release Post on CDF](https://www.databricks.com/blog/2021/06/09/how-to-simplify-cdc-with-delta-lakes-change-data-feed.html)

---
## CDC on Databricks with Declarative Pipelines
**Change Data Capture (CDC)** in Delta Live Tables (DLT) is a feature designed to make it easier, more efficient, and reliable to track and process only the changes—*inserts*, *updates*, and *deletes*—from source data instead of ingesting or reprocessing entire datasets.

### Key CDC Features Introduced in Delta Live Tables

- **Incremental Change Tracking**: DLT can identify and process only the changed records by leveraging techniques such as transaction log monitoring or version/timestamp tracking. This enables highly efficient pipelines with reduced processing load compared to full-table reloads[1].

- **Declarative CDC APIs**: Developers can use high-level, declarative syntax (such as `apply_changes`) to easily define how a target table should reflect the changes from a source, handling complex scenarios (like SCD Type 1 and Type 2) with much less code[1][2].

- **Real-Time and Batch Support**: CDC in DLT works with both real-time streaming and batch data sources. This is useful for applications needing up-to-date data as well as those processing large historical batches[1][2].

- **Automated Schema Evolution**: DLT automatically handles changes in the structure (schema) of source tables, making pipelines more robust as underlying systems evolve[1].

- **Data Quality Enforcement**: With `expectations` decorators, you can specify data quality constraints that are enforced as changes are applied, ensuring data integrity throughout the CDC process[1].

- **Change Data Feed Integration**: Target DLT tables support the Delta Lake "change data feed," making it simple to consume change events downstream or trigger more event-driven logic further along your pipelines[3][5].

- **Full Auditability & Lineage**: Every change can be tracked, with comprehensive metadata including operation type (insert/update/delete), timestamps, and before/after values, enabling detailed audit trails and supporting regulatory compliance[1][3].

- **Seamless Medallion Architecture Compatibility**: The CDC pattern fits naturally within the Databricks medallion architecture, allowing changes in bronze (raw), silver (refined), and gold (aggregated) layers to be processed efficiently and transparently[1][6].

- **Operational Reliability**: Built-in error handling, automated recovery, and operational dashboards allow pipelines to remain robust and manageable even as data volumes and change rates increase[1].

### Usage Example

- You can use DLT CDC features to keep a target "customer" table up to date with changes (including insertions, deletions, and updates) from an operational system, with minimal latency and efficient resource consumption.
- CDC logic in DLT abstracts away the complex SQL or Python merge operations and instead provides easy-to-use functions and decorators[1].

### Table: CDC in Traditional ETL vs. Databricks DLT

| Capability                  | Traditional ETL CDC   | Databricks DLT CDC                  |
|-----------------------------|----------------------|-------------------------------------|
| Code Complexity             | High (custom scripts)| Low (declarative API)               |
| Real-Time Processing        | Limited/manual       | Built-in structured streaming       |
| Schema Evolution           | Manual/error-prone   | Automated                           |
| Data Quality Enforcement    | External tools needed| Native in DLT via expectations      |
| Metadata/Lineage            | Manual/limited       | Automatic tracking                  |
| Operational Maintenance     | High overhead        | Low, managed pipelines              |
| Auditability                | Manual logging       | Built-in with change data feed      |

### Typical Use Cases

- Data replication between OLTP (transactional) and analytical systems with minimal lag.
- Building fact tables that require always-current data for analytics.
- Event-driven workflows, such as responding to important changes in financial or IoT data in real-time[1][2][3].

Delta Live Tables has made CDC a **first-class, managed experience**, blending the ease of declarative setup with the scalability and robustness required for modern data engineering[1][2][3][5].

[1] https://dateonic.com/change-data-capture-cdc-in-databricks-with-delta-live-tables/
[2] https://www.databricks.com/resources/demos/tutorials/lakehouse-platform/cdc-pipeline-with-delta-live-table
[3] https://docs.databricks.com/aws/en/dlt/cdc
[4] https://www.databricks.com/blog/how-perform-change-data-capture-cdc-full-table-snapshots-using-delta-live-tables
[5] https://learn.microsoft.com/en-us/azure/databricks/dlt/cdc
[6] https://community.databricks.com/t5/knowledge-sharing-hub/simplifying-cdc-with-databricks-delta-live-tables-amp-snapshots/td-p/89544
[7] https://stackoverflow.com/questions/79143704/delta-live-tables-cdc
[8] https://github.com/databricks/delta-live-tables-notebooks/blob/main/change-data-capture-example/notebooks/2-Retail_DLT_CDC_Python.py
[9] https://www.reddit.com/r/databricks/comments/1jb181k/are_delta_live_tables_worth_it/

---
## Updating Data in CDC Pipelines
In Databricks Delta Live Tables (DLT) with declarative streaming pipelines, updates and deletes work differently than in traditional batch processing:

**Streaming Tables - Limited Direct Modifications**
For pure streaming tables defined with `CREATE OR REFRESH STREAMING TABLE`, you cannot directly perform UPDATE or DELETE operations. These are designed to be append-only by nature to maintain streaming semantics and ordering guarantees.

**Materialized Views - Change Data Capture (CDC)**
However, you can handle updates and deletes through Change Data Capture patterns:

```sql
CREATE OR REFRESH STREAMING TABLE user_changes
AS SELECT * FROM STREAM(source_table)

CREATE OR REFRESH MATERIALIZED VIEW current_users AS
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY timestamp DESC) as rn
  FROM user_changes
  WHERE operation != 'DELETE'
) WHERE rn = 1
```

**Apply Changes API**
Databricks provides the `APPLY CHANGES` operation specifically for handling CDC scenarios in streaming contexts:

```sql
CREATE OR REFRESH STREAMING TABLE target_table;

APPLY CHANGES INTO LIVE.target_table
FROM STREAM(LIVE.source_changes)
KEYS (user_id)
APPLY AS DELETE WHEN operation = 'DELETE'
APPLY AS TRUNCATE WHEN operation = 'TRUNCATE'
SEQUENCE BY timestamp
```

**Key Points**
- **Streaming tables**: Append-only, no direct updates/deletes
- **Materialized views**: Can implement update logic through window functions and CDC patterns
- **APPLY CHANGES**: Purpose-built for handling updates/deletes in streaming pipelines
- **Delta format**: Underlying Delta format supports ACID operations, but streaming semantics restrict direct modifications

The declarative nature means you define the desired end state, and DLT figures out how to incrementally maintain it, including handling late-arriving updates and maintaining consistency.
