# T-SQL Dynamic SQL Basics
A comprehensive cheatsheet for running dynamic SQL in Microsoft SQL Server that covers the essential techniques and best practices.I've created a comprehensive cheatsheet for dynamic SQL in Microsoft SQL Server that covers everything from basic syntax to advanced techniques. There are other tricks to efficiently build dynamic SQL strings as well, involving tempt table, indexes, and system tables.

The cheatsheet includes:
**Key sections covered:**
- Basic syntax using both EXEC() and sp_executesql methods
- Parameter handling (single, multiple, and output parameters)
- Common use cases like dynamic table names, columns, and WHERE conditions
- Security best practices to prevent SQL injection
- Advanced techniques including complex query building and dynamic pivots
- Performance considerations and error handling
- Common anti-patterns to avoid

**Main takeaways:**
- Always prefer `sp_executesql` over `EXEC()` for better security and plan reuse
- Use parameterized queries to prevent SQL injection
- Apply `QUOTENAME()` for dynamic identifiers
- Validate inputs before executing dynamic SQL

The cheatsheet provides practical examples for each concept, making it easy to reference and implement in your SQL Server projects. Would you like me to expand on any particular section or add additional examples for specific scenarios?

---
# MSSQL Dynamic SQL Cheatsheet

## Basic Syntax

### EXEC() Method
```sql
DECLARE @sql NVARCHAR(MAX)
SET @sql = 'SELECT * FROM Users WHERE UserID = 1'
EXEC(@sql)
```

### sp_executesql Method (Recommended)
```sql
DECLARE @sql NVARCHAR(MAX)
SET @sql = N'SELECT * FROM Users WHERE UserID = @UserID'
EXEC sp_executesql @sql, N'@UserID INT', @UserID = 1
```

## Parameter Handling

### Single Parameter
```sql
DECLARE @sql NVARCHAR(MAX)
DECLARE @UserID INT = 123

SET @sql = N'SELECT * FROM Users WHERE UserID = @UserID'
EXEC sp_executesql @sql, N'@UserID INT', @UserID = @UserID
```

### Multiple Parameters
```sql
DECLARE @sql NVARCHAR(MAX)
DECLARE @UserID INT = 123
DECLARE @Status NVARCHAR(50) = 'Active'

SET @sql = N'SELECT * FROM Users WHERE UserID = @UserID AND Status = @Status'
EXEC sp_executesql @sql, 
    N'@UserID INT, @Status NVARCHAR(50)', 
    @UserID = @UserID, 
    @Status = @Status
```

### Output Parameters
```sql
DECLARE @sql NVARCHAR(MAX)
DECLARE @UserCount INT

SET @sql = N'SELECT @Count = COUNT(*) FROM Users WHERE Status = @Status'
EXEC sp_executesql @sql, 
    N'@Status NVARCHAR(50), @Count INT OUTPUT', 
    @Status = 'Active', 
    @Count = @UserCount OUTPUT

SELECT @UserCount AS TotalUsers
```

## Common Use Cases

### Dynamic Table Names
```sql
DECLARE @TableName NVARCHAR(128) = 'Users'
DECLARE @sql NVARCHAR(MAX)

SET @sql = N'SELECT * FROM ' + QUOTENAME(@TableName)
EXEC sp_executesql @sql
```

### Dynamic Column Names
```sql
DECLARE @ColumnName NVARCHAR(128) = 'UserName'
DECLARE @sql NVARCHAR(MAX)

SET @sql = N'SELECT ' + QUOTENAME(@ColumnName) + N' FROM Users'
EXEC sp_executesql @sql
```

### Dynamic WHERE Conditions
```sql
DECLARE @sql NVARCHAR(MAX)
DECLARE @WhereClause NVARCHAR(500) = ''

-- Build WHERE clause conditionally
IF @UserID IS NOT NULL
    SET @WhereClause = @WhereClause + ' AND UserID = @UserID'
    
IF @Status IS NOT NULL
    SET @WhereClause = @WhereClause + ' AND Status = @Status'

-- Remove leading AND
IF LEN(@WhereClause) > 0
    SET @WhereClause = 'WHERE ' + SUBSTRING(@WhereClause, 6, LEN(@WhereClause))

SET @sql = N'SELECT * FROM Users ' + @WhereClause
EXEC sp_executesql @sql, N'@UserID INT, @Status NVARCHAR(50)', @UserID, @Status
```

### Dynamic ORDER BY
```sql
DECLARE @sql NVARCHAR(MAX)
DECLARE @OrderBy NVARCHAR(128) = 'UserName'
DECLARE @SortOrder NVARCHAR(4) = 'ASC'

SET @sql = N'SELECT * FROM Users ORDER BY ' + QUOTENAME(@OrderBy) + ' ' + @SortOrder
EXEC sp_executesql @sql
```

## Security Best Practices

### Use QUOTENAME for Identifiers
```sql
-- Safe way to handle dynamic identifiers
DECLARE @TableName NVARCHAR(128) = 'Users'
DECLARE @sql NVARCHAR(MAX)

SET @sql = N'SELECT * FROM ' + QUOTENAME(@TableName)
EXEC sp_executesql @sql
```

### Validate Input Parameters
```sql
DECLARE @TableName NVARCHAR(128) = 'Users'
DECLARE @sql NVARCHAR(MAX)

-- Validate table exists
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = @TableName)
BEGIN
    RAISERROR('Invalid table name', 16, 1)
    RETURN
END

SET @sql = N'SELECT * FROM ' + QUOTENAME(@TableName)
EXEC sp_executesql @sql
```

### Use Parameterized Queries
```sql
-- GOOD - Parameterized
DECLARE @sql NVARCHAR(MAX)
SET @sql = N'SELECT * FROM Users WHERE UserName = @UserName'
EXEC sp_executesql @sql, N'@UserName NVARCHAR(50)', @UserName = 'john.doe'

-- BAD - String concatenation (SQL injection risk)
-- SET @sql = N'SELECT * FROM Users WHERE UserName = ''' + @UserName + ''''
```

## Advanced Techniques

### Building Complex Queries
```sql
DECLARE @sql NVARCHAR(MAX) = N''
DECLARE @SelectClause NVARCHAR(500) = N'SELECT UserID, UserName'
DECLARE @FromClause NVARCHAR(500) = N'FROM Users u'
DECLARE @JoinClause NVARCHAR(500) = N'LEFT JOIN Orders o ON u.UserID = o.UserID'
DECLARE @WhereClause NVARCHAR(500) = N'WHERE u.Status = @Status'
DECLARE @OrderClause NVARCHAR(500) = N'ORDER BY u.UserName'

SET @sql = @SelectClause + N' ' + @FromClause + N' ' + @JoinClause + N' ' + @WhereClause + N' ' + @OrderClause

EXEC sp_executesql @sql, N'@Status NVARCHAR(50)', @Status = 'Active'
```

### Dynamic Pivot
```sql
DECLARE @sql NVARCHAR(MAX)
DECLARE @PivotColumns NVARCHAR(MAX)

-- Get pivot columns dynamically
SELECT @PivotColumns = STUFF((
    SELECT DISTINCT ',' + QUOTENAME(Category)
    FROM Products
    FOR XML PATH(''), TYPE
).value('.', 'NVARCHAR(MAX)'), 1, 1, '')

SET @sql = N'
SELECT * FROM (
    SELECT ProductName, Category, Price
    FROM Products
) AS SourceTable
PIVOT (
    AVG(Price) FOR Category IN (' + @PivotColumns + ')
) AS PivotTable'

EXEC sp_executesql @sql
```

### Cursor with Dynamic SQL
```sql
DECLARE @sql NVARCHAR(MAX)
DECLARE @TableName NVARCHAR(128)

DECLARE table_cursor CURSOR FOR
    SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'

OPEN table_cursor
FETCH NEXT FROM table_cursor INTO @TableName

WHILE @@FETCH_STATUS = 0
BEGIN
    SET @sql = N'SELECT COUNT(*) AS RecordCount, ''' + @TableName + ''' AS TableName FROM ' + QUOTENAME(@TableName)
    EXEC sp_executesql @sql
    
    FETCH NEXT FROM table_cursor INTO @TableName
END

CLOSE table_cursor
DEALLOCATE table_cursor
```

## Performance Considerations

### Plan Reuse
```sql
-- Use sp_executesql for better plan reuse
DECLARE @sql NVARCHAR(MAX)
SET @sql = N'SELECT * FROM Users WHERE UserID = @UserID'
EXEC sp_executesql @sql, N'@UserID INT', @UserID = @UserID
```

### Avoid Excessive String Concatenation
```sql
-- Use table variable for complex string building
DECLARE @SqlParts TABLE (ID INT IDENTITY(1,1), SqlPart NVARCHAR(MAX))

INSERT INTO @SqlParts (SqlPart) VALUES (N'SELECT u.UserID, u.UserName')
INSERT INTO @SqlParts (SqlPart) VALUES (N'FROM Users u')
INSERT INTO @SqlParts (SqlPart) VALUES (N'WHERE u.Status = @Status')

DECLARE @sql NVARCHAR(MAX)
SELECT @sql = COALESCE(@sql + N' ', N'') + SqlPart
FROM @SqlParts
ORDER BY ID

EXEC sp_executesql @sql, N'@Status NVARCHAR(50)', @Status = 'Active'
```

## Error Handling

### Try-Catch with Dynamic SQL
```sql
DECLARE @sql NVARCHAR(MAX)
DECLARE @ErrorMessage NVARCHAR(4000)

BEGIN TRY
    SET @sql = N'SELECT * FROM NonExistentTable'
    EXEC sp_executesql @sql
END TRY
BEGIN CATCH
    SET @ErrorMessage = ERROR_MESSAGE()
    PRINT 'Error executing dynamic SQL: ' + @ErrorMessage
END CATCH
```

### Validation Before Execution
```sql
DECLARE @sql NVARCHAR(MAX)
DECLARE @TableName NVARCHAR(128) = 'Users'

-- Check if table exists
IF OBJECT_ID(@TableName) IS NULL
BEGIN
    PRINT 'Table does not exist: ' + @TableName
    RETURN
END

SET @sql = N'SELECT * FROM ' + QUOTENAME(@TableName)
EXEC sp_executesql @sql
```

## Common Anti-Patterns to Avoid

### ❌ String Concatenation with User Input
```sql
-- DON'T DO THIS - SQL Injection risk
DECLARE @UserName NVARCHAR(50) = 'john.doe'
DECLARE @sql NVARCHAR(MAX)
SET @sql = N'SELECT * FROM Users WHERE UserName = ''' + @UserName + ''''
```

### ❌ Using EXEC() Instead of sp_executesql
```sql
-- Less secure and no plan reuse
EXEC('SELECT * FROM Users WHERE UserID = ' + CAST(@UserID AS NVARCHAR(10)))
```

### ❌ Not Using QUOTENAME for Identifiers
```sql
-- Vulnerable to SQL injection
SET @sql = N'SELECT * FROM ' + @TableName
```

## Quick Reference

| Task | Method | Security Level |
|------|--------|----------------|
| Execute simple query | `EXEC(@sql)` | Low |
| Execute with parameters | `sp_executesql` | High |
| Dynamic table names | `QUOTENAME(@table)` | High |
| Dynamic columns | `QUOTENAME(@column)` | High |
| User input in WHERE | Parameters only | High |
| Building complex queries | String concatenation + params | Medium |

## Key Takeaways

1. **Always use sp_executesql** instead of EXEC() when possible
2. **Parameterize user input** - never concatenate user input directly
3. **Use QUOTENAME()** for dynamic identifiers (tables, columns)
4. **Validate inputs** before building queries
5. **Consider performance** - dynamic SQL can prevent plan reuse
6. **Handle errors** appropriately with TRY-CATCH blocks
7. **Test thoroughly** - dynamic SQL is harder to debug
