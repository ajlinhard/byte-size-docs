# Lakeflow Change Data Capture (CDC)
When upstream data is changing in a live OLTP system or ML/Window functions prepartion there may be a need to update downstream data accordingly. This is where the concept of CDC comes into play. Traditionally, this was done with the MERGE or MERGE INTO statement, but this can become complex if multiple changes are coming in for the same record ID. Thus with deduplication or other row reduction techniques CDC can become more lengthy. Also, the type of CDC you need can increase or decrease complex.

This is the reason for Databricks attempting to simplify the CDC with the APPLY CHANGED INTO command. With the goal of simplifying syntax and increasing performance.

### Documentation
- [Databricks - What is CDC?](https://docs.databricks.com/aws/en/dlt/what-is-change-data-capture)
- [Databricks - AUTO CDC API](https://docs.databricks.com/aws/en/dlt/cdc?language=Python)
- [Databricks - Delta Change Data Feeds (CDF)](https://docs.databricks.com/aws/en/delta/delta-change-data-feed)

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
