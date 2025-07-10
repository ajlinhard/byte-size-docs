# T-SQL File Loading Cheatsheet
This cheatsheet covers the essential commands and techniques for loading data into SQL Server using BULK INSERT and OPENROWSET. The key differences between these methods are:

**BULK INSERT** is better for:
- Simple, direct loading into existing tables
- When you know the exact table structure
- Better performance for straightforward imports

**OPENROWSET** is better for:
- Previewing data before loading
- Creating new tables from files
- More flexible data manipulation during import
- When you need to transform data while loading

The cheatsheet includes practical examples, common gotchas, performance optimization tips, and troubleshooting guidance that should help you handle most bulk loading scenarios in SQL Server.

---
# MSSQL Data Loading Cheatsheet: OPENROWSET & BULK INSERT

## Prerequisites & Setup

### Enable Ad Hoc Distributed Queries (for OPENROWSET)
```sql
-- Enable ad hoc distributed queries
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'Ad Hoc Distributed Queries', 1;
RECONFIGURE;
```

### File Permissions
- SQL Server service account needs read access to the file/folder
- Files must be accessible from the SQL Server machine
- Use UNC paths for network locations: `\\server\share\file.csv`

## BULK INSERT

### Basic Syntax
```sql
BULK INSERT [database.]schema.table_name
FROM 'file_path'
WITH (options);
```

### Common Options

#### CSV Files
```sql
BULK INSERT dbo.MyTable
FROM 'C:\Data\myfile.csv'
WITH (
    FIELDTERMINATOR = ',',          -- Column separator
    ROWTERMINATOR = '\n',           -- Row separator
    FIRSTROW = 2,                   -- Skip header row
    CODEPAGE = 'ACP',               -- Character encoding
    DATAFILETYPE = 'char',          -- Data type
    KEEPNULLS,                      -- Preserve NULL values
    TABLOCK                         -- Table lock for performance
);
```

#### Tab-Delimited Files
```sql
BULK INSERT dbo.MyTable
FROM 'C:\Data\myfile.txt'
WITH (
    FIELDTERMINATOR = '\t',
    ROWTERMINATOR = '\n',
    FIRSTROW = 1
);
```

#### Fixed-Width Files
```sql
BULK INSERT dbo.MyTable
FROM 'C:\Data\myfile.txt'
WITH (
    DATAFILETYPE = 'char',
    ROWTERMINATOR = '\n',
    FORMATFILE = 'C:\Data\myformat.fmt'
);
```

### Error Handling
```sql
BULK INSERT dbo.MyTable
FROM 'C:\Data\myfile.csv'
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    MAXERRORS = 10,                 -- Max errors before stopping
    ERRORFILE = 'C:\Logs\errors.txt' -- Error log file
);
```

## OPENROWSET

### Basic Syntax
```sql
SELECT * FROM OPENROWSET(
    BULK 'file_path',
    options
) AS alias;
```

### Query Data Before Loading
```sql
-- Preview CSV data
SELECT * FROM OPENROWSET(
    BULK 'C:\Data\myfile.csv',
    FORMATFILE = 'C:\Data\myformat.fmt',
    FIRSTROW = 2
) AS data;
```

### Load with SELECT INTO
```sql
-- Create new table from file
SELECT * INTO dbo.NewTable
FROM OPENROWSET(
    BULK 'C:\Data\myfile.csv',
    FORMATFILE = 'C:\Data\myformat.fmt',
    FIRSTROW = 2
) AS data;
```

### Insert into Existing Table
```sql
-- Insert into existing table
INSERT INTO dbo.ExistingTable (col1, col2, col3)
SELECT col1, col2, col3
FROM OPENROWSET(
    BULK 'C:\Data\myfile.csv',
    FORMATFILE = 'C:\Data\myformat.fmt',
    FIRSTROW = 2
) AS data;
```

### Single Column (for XML/JSON)
```sql
-- Load single column data (XML, JSON, etc.)
SELECT BulkColumn
FROM OPENROWSET(
    BULK 'C:\Data\myfile.xml',
    SINGLE_CLOB
) AS data;
```

## Format Files

### XML Format File Example
```xml
<?xml version="1.0"?>
<BCPFORMAT xmlns="http://schemas.microsoft.com/sqlserver/2004/bulkload/format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <RECORD>
    <FIELD ID="1" xsi:type="CharTerm" TERMINATOR="," MAX_LENGTH="50"/>
    <FIELD ID="2" xsi:type="CharTerm" TERMINATOR="," MAX_LENGTH="50"/>
    <FIELD ID="3" xsi:type="CharTerm" TERMINATOR="\r\n" MAX_LENGTH="10"/>
  </RECORD>
  <ROW>
    <COLUMN SOURCE="1" NAME="FirstName" xsi:type="SQLVARYCHAR"/>
    <COLUMN SOURCE="2" NAME="LastName" xsi:type="SQLVARYCHAR"/>
    <COLUMN SOURCE="3" NAME="Age" xsi:type="SQLINT"/>
  </ROW>
</BCPFORMAT>
```

### Generate Format File with BCP
```cmd
bcp "SELECT * FROM MyDatabase.dbo.MyTable" queryout dummy.txt -c -T -S ServerName
bcp MyDatabase.dbo.MyTable format nul -c -x -f MyTable.xml -T -S ServerName
```

## Performance Tips

### Optimize for Large Files
```sql
-- Use TABLOCK for better performance
BULK INSERT dbo.MyTable
FROM 'C:\Data\largefile.csv'
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    TABLOCK,                        -- Table lock
    BATCHSIZE = 50000,              -- Batch size
    ROWS_PER_BATCH = 50000          -- Rows per batch
);
```

### Minimal Logging
```sql
-- Ensure database is in SIMPLE or BULK_LOGGED recovery mode
ALTER DATABASE MyDatabase SET RECOVERY BULK_LOGGED;

-- Use appropriate batch sizes for minimal logging
BULK INSERT dbo.MyTable
FROM 'C:\Data\myfile.csv'
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK,
    BATCHSIZE = 1000
);
```

## Common File Formats

### CSV with Quoted Fields
```sql
BULK INSERT dbo.MyTable
FROM 'C:\Data\quoted.csv'
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    FIELDQUOTE = '"',               -- SQL Server 2017+
    FIRSTROW = 2
);
```

### Pipe-Delimited
```sql
BULK INSERT dbo.MyTable
FROM 'C:\Data\myfile.txt'
WITH (
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '\n',
    FIRSTROW = 1
);
```

### Custom Line Endings
```sql
BULK INSERT dbo.MyTable
FROM 'C:\Data\myfile.txt'
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '|\n',          -- Custom row terminator
    FIRSTROW = 1
);
```

## Error Handling & Troubleshooting

### Common Issues

#### Permission Errors
```sql
-- Check SQL Server service account permissions
-- Ensure file path is accessible from SQL Server machine
-- Use UNC paths for network files
```

#### Data Type Mismatches
```sql
-- Use format files to specify data types
-- Consider staging tables with VARCHAR columns first
-- Use TRY_CONVERT for flexible data conversion
```

#### Character Encoding Issues
```sql
-- Specify appropriate CODEPAGE
BULK INSERT dbo.MyTable
FROM 'C:\Data\myfile.csv'
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    CODEPAGE = '65001',             -- UTF-8
    FIRSTROW = 2
);
```

### Error Logging
```sql
-- Enable detailed error logging
BULK INSERT dbo.MyTable
FROM 'C:\Data\myfile.csv'
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    MAXERRORS = 0,                  -- Log all errors
    ERRORFILE = 'C:\Logs\bulk_errors.txt',
    FIRE_TRIGGERS                   -- Fire triggers if needed
);
```

## Code Pages Reference

| Code Page | Description |
|-----------|-------------|
| ACP       | ANSI/OEM    |
| OEM       | OEM         |
| RAW       | No conversion |
| 1252      | Latin1 (Western European) |
| 65001     | UTF-8       |
| 1200      | UTF-16LE    |
| 1201      | UTF-16BE    |

## Best Practices

1. **Always test with small files first**
2. **Use staging tables for complex transformations**
3. **Monitor transaction log growth**
4. **Consider using SSIS for complex ETL scenarios**
5. **Backup databases before large bulk operations**
6. **Use format files for consistent imports**
7. **Set appropriate batch sizes for memory management**
8. **Consider parallel processing for very large files**

## Quick Reference Commands

```sql
-- Check bulk insert settings
SELECT * FROM sys.configurations WHERE name LIKE '%bulk%';

-- Check file permissions (extended stored procedure)
EXEC xp_fileexist 'C:\Data\myfile.csv';

-- Monitor bulk insert progress
SELECT * FROM sys.dm_exec_requests WHERE command LIKE 'BULK INSERT%';
```
