# Unity Catalog System Tables Cheatsheet

## Overview

Unity Catalog system tables provide metadata and log data related to Databricks operations. System tables are organized into separate schemas containing one or more tables that are owned and updated by Databricks. The storage and cost of system tables are handled by Databricks, while customers pay for the compute used to query them.

## Accessing System Tables

```sql
-- List all system schemas in your account (using Databricks CLI)
databricks unity-catalog system-schemas list --metastore-id <metastore-id>

-- Enable a system schema (using Databricks CLI)
databricks unity-catalog system-schemas enable --metastore-id <metastore-id> --schema <SCHEMA_NAME>

-- Grant permissions to system schemas
GRANT USE SCHEMA ON system.<schema_name> TO <principal>;
GRANT SELECT ON system.<schema_name>.<table_name> TO <principal>;
```

## System Catalog Structure

All system tables are contained in a catalog called `system`, which is included in every Unity Catalog metastore. Inside this catalog, you'll find various schemas that contain the system tables.

## Available System Schemas

### `system.billing`

Contains account-wide billing information (enabled by default).

| Table | Description |
|-------|-------------|
| `billable_usage` | Records for all billable usage across the entire account |
| `list_price` | Current list prices for all Databricks products |
| `historical_pricing` | Historical pricing information |

### `system.compute`

Contains compute-related information (enabled by default).

| Table | Description |
|-------|-------------|
| `clusters` | Full history of cluster configurations for all-purpose and job clusters |
| `cluster_events` | Events related to clusters (creation, termination, etc.) |
| `warehouse_events` | Events related to SQL warehouses |
| `node_types` | Available node types with their hardware specifications |
| `query_history` | Information on SQL commands, I/O performance, and number of rows returned |

### `system.access`

Contains access and audit information.

| Table | Description |
|-------|-------------|
| `audit_logs` | Audit logs of actions performed against the metastore |
| `access_history` | Records of who accessed data and what actions they performed |

### `system.lineage`

Contains data lineage information.

| Table | Description |
|-------|-------------|
| `table_lineage` | Lineage data at the table level |
| `column_lineage` | Lineage data at the column level |

### `system.information_schema`

Contains metadata about tables and their structure.

| Table | Description |
|-------|-------------|
| `tables` | Metadata about tables, including data source format |
| `columns` | Metadata about table columns |
| `views` | Metadata about views |

### `system.storage`

Contains storage optimization information.

| Table | Description |
|-------|-------------|
| `predictive_optimization` | Tracks operation history of optimized tables |

## Common Queries

### List All Tables and Their Data Source Format

```sql
SELECT table_name, data_source_format 
FROM system.information_schema.tables;
```

### List Only Delta Tables

```sql
SELECT table_name, data_source_format 
FROM system.information_schema.tables 
WHERE data_source_format = "DELTA";
```

### Analyze Billable Usage

```sql
SELECT workspace_id, sku, usage_date, usage_quantity, list_price
FROM system.billing.billable_usage
JOIN system.billing.list_price ON billable_usage.sku = list_price.sku
WHERE usage_date > CURRENT_DATE - INTERVAL 30 DAYS
ORDER BY usage_date DESC;
```

### Audit User Activity

```sql
SELECT timestamp, user_identity, action_name, request_params
FROM system.access.audit_logs
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL 7 DAYS
ORDER BY timestamp DESC;
```

### Explore Table Lineage

```sql
SELECT source_table, target_table, transformation_type
FROM system.lineage.table_lineage
WHERE target_catalog = '<your_catalog>' AND target_schema = '<your_schema>';
```

### Analyze Cluster Usage

```sql
SELECT cluster_id, 
       cluster_name, 
       start_time, 
       terminated_time, 
       CAST(terminated_time AS LONG) - CAST(start_time AS LONG) AS runtime_seconds
FROM system.compute.clusters
WHERE terminated_time IS NOT NULL
ORDER BY start_time DESC;
```

## Limitations and Notes

1. System tables are read-only and cannot be modified.
2. System tables contain operational data for all workspaces in your account deployed within the same cloud region.
3. Billing system tables contain account-wide data.
4. The system schemas `system.operational_data` and `system.lineage` are deprecated and will contain empty tables.
5. Some system tables are in Public Preview or Private Preview and might incur charges in the future.
6. Delta Sharing is used to share system table data with customers. For streaming with system tables, set `skipChangeCommits` to `true`.
7. `Trigger.AvailableNow` is not supported with Delta Sharing streaming.
8. System tables are not available in AWS GovCloud regions.

## Security and Access Control

Access to system tables is governed by Unity Catalog. No user has access to system schemas by default. To grant access:

1. A user must be both a metastore admin and an account admin to grant USE and SELECT permissions on system schemas.
2. System tables must be enabled by an account admin using system-schemas commands in the Databricks CLI or using the SystemSchemas API.

## References

- The billing and compute schemas are enabled by default. Other schemas must be enabled manually.
- System tables can only be accessed from a Unity Catalog-enabled workspace, but they include operational data for non-Unity Catalog workspaces in your account.
