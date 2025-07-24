# Delta Lake CDC - via Version History
Yes, when using Delta tables for SCD Type 1, the "deleted" record technically still exists in the underlying storage and can be accessed through Delta's time travel capabilities.

Here's what happens under the hood:

**Delta's Versioning Mechanism** maintains a transaction log that tracks every operation performed on the table. When you perform an SCD Type 1 update (overwriting old values), Delta doesn't physically delete the old data files immediately. Instead, it creates new data files with the updated records and marks the old files as "removed" in the transaction log.

**Time Travel Queries** allow you to access previous versions of the data using syntax like:
```sql
SELECT * FROM my_table VERSION AS OF 5
-- or
SELECT * FROM my_table TIMESTAMP AS OF '2024-01-15 10:30:00'
```

**Physical Storage Reality** means the old record exists in the actual Parquet files on disk until those files are physically removed during a vacuum operation. Before vacuuming, you can query any historical version and see the data exactly as it existed at that point in time.

**Vacuum Operations** are what actually remove the old data files from storage. By default, Delta keeps a 30-day retention period, so you can time travel back up to 30 days. After running `VACUUM`, older versions become inaccessible because the underlying files are deleted.

**Practical Implications** include:
- Storage costs are higher initially since multiple versions exist
- You can recover from accidental overwrites by querying previous versions
- Compliance and audit requirements can be met through historical queries
- Performance may be impacted if too many versions accumulate

This behavior distinguishes Delta tables from traditional databases where SCD Type 1 updates would immediately lose the old values. Delta's architecture provides both the simplicity of SCD Type 1 operations and the safety net of historical data access, at least until vacuum operations clean up the old files.

## Delta Table Retention
You can set the default retention period for a Delta table using several approaches:

## Table-Level Configuration

**At Table Creation Time:**
```sql
CREATE TABLE my_table (
    id INT,
    name STRING,
    updated_at TIMESTAMP
) USING DELTA
TBLPROPERTIES (
    'delta.deletedFileRetentionDuration' = '7 days'
)
```

**For Existing Tables:**
```sql
ALTER TABLE my_table SET TBLPROPERTIES (
    'delta.deletedFileRetentionDuration' = '7 days'
)
```

## Session-Level Configuration

**Set for Current Session:**
```sql
SET spark.databricks.delta.retentionDurationCheck.enabled = false;
SET spark.databricks.delta.vacuum.parallelDelete.enabled = true;
```

**In Spark Configuration:**
```python
spark.conf.set("spark.databricks.delta.properties.defaults.deletedFileRetentionDuration", "7 days")
```

## Available Time Units

Delta accepts various time formats:
- `'7 days'`
- `'168 hours'` 
- `'interval 1 week'`
- `'interval 10080 minutes'`

## Important Considerations

**Minimum Retention Period:** Delta enforces a minimum retention of 7 days by default to prevent accidental data loss. To override this safety check, you need to disable `retentionDurationCheck.enabled`.

**Global vs Table-Specific:** Table-level properties override session or cluster-level defaults. This allows you to have different retention policies for different tables based on their importance or compliance requirements.

**Checking Current Settings:**
```sql
DESCRIBE DETAIL my_table;
-- or
SHOW TBLPROPERTIES my_table;
```

**Manual Vacuum with Custom Retention:**
```sql
VACUUM my_table RETAIN 3 HOURS;
```

The retention setting only affects when files become eligible for deletion during vacuum operations - it doesn't automatically delete files. You still need to run `VACUUM` commands to actually reclaim the storage space.
