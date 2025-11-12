# Tablespaces in PostgreSQL

A **tablespace** in PostgreSQL is a location on the file system where database objects (tables, indexes) are physically stored. It allows you to control where data is stored on disk, separate from the default data directory.

## Purpose and Benefits

1. **Storage Management** - Store data across multiple disks/partitions
2. **Performance Optimization** - Place frequently accessed tables on faster storage (SSDs)
3. **Space Management** - Move large tables to disks with more space
4. **I/O Distribution** - Distribute I/O load across multiple storage devices

---

## Syntax and Usage

### Create a Tablespace
```sql
CREATE TABLESPACE tablespace_name
    OWNER username
    LOCATION '/path/to/directory';
```

**Important:** The directory must:
- Exist on the file system
- Be empty
- Be owned by the PostgreSQL system user (usually `postgres`)
- Have proper permissions

### Create Table in a Tablespace
```sql
CREATE TABLE table_name (
    id INT,
    name VARCHAR(100)
) TABLESPACE tablespace_name;
```

### Create Index in a Tablespace
```sql
CREATE INDEX index_name 
ON table_name (column_name) 
TABLESPACE tablespace_name;
```

### Move Existing Object to Different Tablespace
```sql
ALTER TABLE table_name SET TABLESPACE new_tablespace_name;
ALTER INDEX index_name SET TABLESPACE new_tablespace_name;
```

### Set Default Tablespace for Database
```sql
ALTER DATABASE database_name SET TABLESPACE tablespace_name;
-- or set default for new objects
SET default_tablespace = tablespace_name;
```

---

## View Existing Tablespaces

```sql
-- List all tablespaces
\db

-- Or query system catalog
SELECT * FROM pg_tablespace;

-- See which tablespace an object uses
SELECT tablename, tablespace 
FROM pg_tables 
WHERE schemaname = 'public';
```

---

## Default Tablespaces

PostgreSQL has two default tablespaces:
- **`pg_default`** - Default for user data
- **`pg_global`** - For system catalogs

---

## Drop a Tablespace
```sql
DROP TABLESPACE tablespace_name;
```
*Note: Must be empty before dropping*

---

## Example Use Case

```sql
-- Create tablespace on SSD for hot data
CREATE TABLESPACE fast_storage 
    LOCATION '/mnt/ssd/postgres';

-- Create tablespace on HDD for archive data
CREATE TABLESPACE archive_storage 
    LOCATION '/mnt/hdd/postgres';

-- Place active orders on SSD
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE
) TABLESPACE fast_storage;

-- Place order history on HDD
CREATE TABLE orders_archive (
    order_id INT,
    customer_id INT,
    order_date DATE
) TABLESPACE archive_storage;
```
