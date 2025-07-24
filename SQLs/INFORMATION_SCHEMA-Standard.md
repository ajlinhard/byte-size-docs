# INFORMATION SCHEMA Standard
Yes, system tables are typically part of a metastore, and the information schema is indeed a standard.

**System Tables and Metastores:**
System tables (also called catalog tables or metadata tables) store information about the database structure itself - things like table definitions, column metadata, indexes, constraints, user permissions, and other administrative data. In most database systems, these system tables are a core component of the metastore, which is the centralized repository that holds all metadata about the database objects.

**Information Schema Standard:**
The INFORMATION_SCHEMA is a standardized set of read-only views defined by the SQL standard (ISO/IEC 9075). It provides a uniform way to access metadata across different database systems. The standard defines specific view names and structures like:

- `INFORMATION_SCHEMA.TABLES` - information about tables
- `INFORMATION_SCHEMA.COLUMNS` - column definitions  
- `INFORMATION_SCHEMA.CONSTRAINTS` - constraint information
- `INFORMATION_SCHEMA.ROUTINES` - stored procedures and functions

Most major database systems implement some version of the information schema standard, though they often extend it with their own additional views and columns. For example, PostgreSQL, MySQL, SQL Server, and others all provide INFORMATION_SCHEMA views, making it easier to write portable queries for metadata discovery.

However, each database system also typically has its own native system catalog tables (like PostgreSQL's `pg_catalog` schema or MySQL's `mysql` database) that may provide more detailed or system-specific information than what's available through the standardized information schema views.

---
# Standard List of Tables and Columns
The SQL standard defines several required views in the INFORMATION_SCHEMA, though the exact set has evolved across different versions of the standard (SQL-92, SQL:1999, SQL:2003, etc.). Here are the core standard views and their key columns:

**INFORMATION_SCHEMA.SCHEMATA**
- CATALOG_NAME
- SCHEMA_NAME
- SCHEMA_OWNER
- DEFAULT_CHARACTER_SET_CATALOG
- DEFAULT_CHARACTER_SET_SCHEMA
- DEFAULT_CHARACTER_SET_NAME

**INFORMATION_SCHEMA.TABLES**
- TABLE_CATALOG
- TABLE_SCHEMA
- TABLE_NAME
- TABLE_TYPE (BASE TABLE, VIEW, etc.)

**INFORMATION_SCHEMA.COLUMNS**
- TABLE_CATALOG
- TABLE_SCHEMA
- TABLE_NAME
- COLUMN_NAME
- ORDINAL_POSITION
- COLUMN_DEFAULT
- IS_NULLABLE
- DATA_TYPE
- CHARACTER_MAXIMUM_LENGTH
- CHARACTER_OCTET_LENGTH
- NUMERIC_PRECISION
- NUMERIC_SCALE
- DATETIME_PRECISION

**INFORMATION_SCHEMA.VIEWS**
- TABLE_CATALOG
- TABLE_SCHEMA
- TABLE_NAME
- VIEW_DEFINITION
- CHECK_OPTION
- IS_UPDATABLE

**INFORMATION_SCHEMA.TABLE_CONSTRAINTS**
- CONSTRAINT_CATALOG
- CONSTRAINT_SCHEMA
- CONSTRAINT_NAME
- TABLE_CATALOG
- TABLE_SCHEMA
- TABLE_NAME
- CONSTRAINT_TYPE

**INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE**
- TABLE_CATALOG
- TABLE_SCHEMA
- TABLE_NAME
- COLUMN_NAME
- CONSTRAINT_CATALOG
- CONSTRAINT_SCHEMA
- CONSTRAINT_NAME

The standard also defines views for domains, character sets, collations, routines (stored procedures/functions), and privileges, though implementations vary significantly in what they actually provide. Many database systems implement a subset of these and add their own extensions.
