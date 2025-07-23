# Unity Catalog System Tables and Commands Cheatsheet
The cheatsheet is organized by object type (catalogs, schemas, tables, views, volumes, functions) and includes:

- **Basic operations** for listing, describing, and managing each object type
- **Information schema queries** for programmatic metadata access
- **System tables** for lineage, auditing, and billing
- **Permission management** commands
- **Utility queries** for common exploration tasks
- **Best practices** and tips

This should serve as a handy reference for navigating Unity Catalog's three-level namespace (`catalog.schema.object`) and performing common administrative and exploratory tasks. You can bookmark this cheatsheet and refer to it whenever you're working with Unity Catalog in Databricks!

### Documentations:
- [Databricks Monitoring System Tables](https://docs.databricks.com/aws/en/admin/system-tables#monitor-usage-with-system-tables)
- [Databricks Information Schema Tables](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-information-schema)

## Hierarchy Overview
Unity Catalog follows a three-level namespace: `catalog.schema.object`

## Catalog Operations

### List All Catalogs
```sql
SHOW CATALOGS;
```

### Get Current Catalog
```sql
SELECT current_catalog();
```

### Set Current Catalog
```sql
USE CATALOG catalog_name;
```

### Show Catalog Details
```sql
DESCRIBE CATALOG catalog_name;
DESCRIBE CATALOG EXTENDED catalog_name;
```

### Create Catalog
```sql
CREATE CATALOG catalog_name 
COMMENT 'Optional description';
```

### Drop Catalog
```sql
DROP CATALOG catalog_name CASCADE;
```

## Schema Operations

### List All Schemas in Current Catalog
```sql
SHOW SCHEMAS;
SHOW DATABASES;  -- Alternative syntax
```

### List Schemas in Specific Catalog
```sql
SHOW SCHEMAS IN catalog_name;
```

### Get Current Schema
```sql
SELECT current_schema();
SELECT current_database();  -- Alternative
```

### Set Current Schema
```sql
USE SCHEMA catalog_name.schema_name;
USE catalog_name.schema_name;  -- Alternative
```

### Show Schema Details
```sql
DESCRIBE SCHEMA catalog_name.schema_name;
DESCRIBE SCHEMA EXTENDED catalog_name.schema_name;
```

### Create Schema
```sql
CREATE SCHEMA catalog_name.schema_name
COMMENT 'Optional description'
LOCATION 's3://bucket/path/';  -- Optional for external location
```

### Drop Schema
```sql
DROP SCHEMA catalog_name.schema_name CASCADE;
```

## Table Operations

### List All Tables in Current Schema
```sql
SHOW TABLES;
```

### List Tables in Specific Schema
```sql
SHOW TABLES IN catalog_name.schema_name;
```

### Show Table Details
```sql
DESCRIBE TABLE catalog_name.schema_name.table_name;
DESCRIBE TABLE EXTENDED catalog_name.schema_name.table_name;
DESCRIBE FORMATTED catalog_name.schema_name.table_name;
```

### Show Table Schema/Columns
```sql
DESCRIBE catalog_name.schema_name.table_name;
SHOW COLUMNS IN catalog_name.schema_name.table_name;
```

### Show Table Properties
```sql
SHOW TBLPROPERTIES catalog_name.schema_name.table_name;
```

### Show Table History (Delta tables)
```sql
DESCRIBE HISTORY catalog_name.schema_name.table_name;
```

### Show Table Statistics
```sql
ANALYZE TABLE catalog_name.schema_name.table_name COMPUTE STATISTICS;
DESCRIBE EXTENDED catalog_name.schema_name.table_name;
```

## View Operations

### List All Views
```sql
SHOW VIEWS;
SHOW VIEWS IN catalog_name.schema_name;
```

### Show View Definition
```sql
SHOW CREATE TABLE catalog_name.schema_name.view_name;
```

### Describe View
```sql
DESCRIBE VIEW catalog_name.schema_name.view_name;
```

## Volume Operations (Unity Catalog Volumes)

### List Volumes
```sql
SHOW VOLUMES;
SHOW VOLUMES IN catalog_name.schema_name;
```

### Show Volume Details
```sql
DESCRIBE VOLUME catalog_name.schema_name.volume_name;
```

### Create Volume
```sql
CREATE VOLUME catalog_name.schema_name.volume_name
COMMENT 'Optional description';
```

## Function Operations

### List Functions
```sql
SHOW FUNCTIONS;
SHOW FUNCTIONS IN catalog_name.schema_name;
```

### Show Function Details
```sql
DESCRIBE FUNCTION catalog_name.schema_name.function_name;
DESCRIBE FUNCTION EXTENDED catalog_name.schema_name.function_name;
```

### Show Function Definition
```sql
SHOW CREATE FUNCTION catalog_name.schema_name.function_name;
```

## Information Schema Queries

### Query All Objects in Catalog
```sql
SELECT * FROM system.information_schema.catalogs 
WHERE catalog_name = 'your_catalog';
```

### Query All Schemas
```sql
SELECT * FROM system.information_schema.schemata 
WHERE catalog_name = 'your_catalog';
```

### Query All Tables
```sql
SELECT * FROM system.information_schema.tables 
WHERE table_catalog = 'your_catalog' 
AND table_schema = 'your_schema';
```

### Query All Columns
```sql
SELECT * FROM system.information_schema.columns 
WHERE table_catalog = 'your_catalog' 
AND table_schema = 'your_schema' 
AND table_name = 'your_table';
```

### Query All Views
```sql
SELECT * FROM system.information_schema.views 
WHERE table_catalog = 'your_catalog';
```

### Query All Functions
```sql
SELECT * FROM system.information_schema.routines 
WHERE routine_catalog = 'your_catalog';
```

## System Tables for Unity Catalog

### Table Lineage
```sql
SELECT * FROM system.access.table_lineage 
WHERE source_table_full_name = 'catalog.schema.table';
```

### Column Lineage
```sql
SELECT * FROM system.access.column_lineage 
WHERE source_table_full_name = 'catalog.schema.table';
```

### Access Audit Logs
```sql
SELECT * FROM system.access.audit 
WHERE workspace_id = 'your_workspace_id'
AND event_date >= '2024-01-01';
```

### Billing Usage
```sql
SELECT * FROM system.billing.usage 
WHERE workspace_id = 'your_workspace_id'
AND usage_date >= '2024-01-01';
```

## Permissions and Grants

### Show Grants on Object
```sql
SHOW GRANTS ON CATALOG catalog_name;
SHOW GRANTS ON SCHEMA catalog_name.schema_name;
SHOW GRANTS ON TABLE catalog_name.schema_name.table_name;
```

### Grant Permissions
```sql
GRANT USE CATALOG ON CATALOG catalog_name TO user_or_group;
GRANT USE SCHEMA ON SCHEMA catalog_name.schema_name TO user_or_group;
GRANT SELECT ON TABLE catalog_name.schema_name.table_name TO user_or_group;
```

### Revoke Permissions
```sql
REVOKE USE CATALOG ON CATALOG catalog_name FROM user_or_group;
REVOKE SELECT ON TABLE catalog_name.schema_name.table_name FROM user_or_group;
```

## Useful Utility Queries

### Find All Tables Across Catalogs
```sql
SELECT table_catalog, table_schema, table_name, table_type
FROM system.information_schema.tables
ORDER BY table_catalog, table_schema, table_name;
```

### Find Tables by Pattern
```sql
SELECT table_catalog, table_schema, table_name
FROM system.information_schema.tables
WHERE table_name LIKE '%customer%';
```

### Get Table Sizes (requires compute statistics)
```sql
SELECT table_catalog, table_schema, table_name,
       size_in_bytes, num_rows
FROM system.information_schema.tables
WHERE table_catalog = 'your_catalog'
ORDER BY size_in_bytes DESC;
```

### Find Empty Tables
```sql
SELECT table_catalog, table_schema, table_name
FROM system.information_schema.tables
WHERE num_rows = 0 OR num_rows IS NULL;
```

### List All Objects in Current Context
```sql
-- Current catalog and schema
SELECT current_catalog() as current_catalog, 
       current_schema() as current_schema;

-- All tables in current schema
SHOW TABLES;

-- All views in current schema  
SHOW VIEWS;

-- All functions in current schema
SHOW FUNCTIONS;
```

## Tips and Best Practices

1. **Always use three-part naming** (`catalog.schema.object`) for clarity and avoid ambiguity
2. **Use EXTENDED or FORMATTED** with DESCRIBE for more detailed information
3. **Query system.information_schema** for programmatic access to metadata
4. **Check permissions** with SHOW GRANTS before attempting operations
5. **Use current_catalog() and current_schema()** to verify your current context
6. **Leverage system tables** for lineage, auditing, and billing information
7. **Use LIKE patterns** in information_schema queries to find objects by naming conventions
