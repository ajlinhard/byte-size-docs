# MSSQL PIVOT and UNPIVOT Cheatsheet

## PIVOT Overview
PIVOT transforms rows into columns by rotating unique values from one column into multiple columns and performing aggregations.

### PIVOT Syntax
```sql
SELECT <non-pivoted column>, 
       [first pivoted column] AS <column name>,
       [second pivoted column] AS <column name>,
       ...
       [last pivoted column] AS <column name>
FROM (
    <SELECT query that produces the data>
) AS <alias for the source query>
PIVOT (
    <aggregation function>(<column being aggregated>)
    FOR <column that contains the values that will become column headers>
        IN ([first pivoted column], [second pivoted column], ... [last pivoted column])
) AS <alias for the pivot table>
```

### PIVOT Components Breakdown
- **Source Query**: The subquery that provides the data to be pivoted
- **Aggregation Function**: SUM, COUNT, AVG, MIN, MAX, etc.
- **Column Being Aggregated**: The values that will be summarized
- **FOR Column**: The column whose unique values become new column headers
- **IN Clause**: Specifies which values to pivot (must be literals or variables)

## UNPIVOT Overview
UNPIVOT transforms columns into rows by rotating column values into a single column.

### UNPIVOT Syntax
```sql
SELECT <columns>
FROM (
    <SELECT query that produces the data>
) AS <alias>
UNPIVOT (
    <values column> FOR <names column>
    IN ([first column], [second column], ... [last column])
) AS <alias for unpivot table>
```

### UNPIVOT Components Breakdown
- **Values Column**: The new column that will contain the unpivoted values
- **Names Column**: The new column that will contain the original column names
- **IN Clause**: Specifies which columns to unpivot

---

## PIVOT Examples

### Test Data Setup
```sql
-- Create sample sales data
CREATE TABLE #Sales (
    SalesPerson VARCHAR(50),
    Region VARCHAR(50),
    SalesAmount DECIMAL(10,2)
);

INSERT INTO #Sales VALUES
('John', 'North', 1000),
('John', 'South', 1500),
('John', 'East', 800),
('Mary', 'North', 1200),
('Mary', 'South', 900),
('Mary', 'East', 1100),
('Bob', 'North', 800),
('Bob', 'South', 1300),
('Bob', 'East', 950);
```

### Example 1: Basic PIVOT
Transform regions from rows to columns, showing total sales by person and region.

```sql
SELECT SalesPerson, 
       [North], 
       [South], 
       [East]
FROM (
    SELECT SalesPerson, Region, SalesAmount
    FROM #Sales
) AS SourceTable
PIVOT (
    SUM(SalesAmount)
    FOR Region IN ([North], [South], [East])
) AS PivotTable;
```

**Result:**
```
SalesPerson | North | South | East
------------|-------|-------|------
Bob         | 800   | 1300  | 950
John        | 1000  | 1500  | 800
Mary        | 1200  | 900   | 1100
```

### Example 2: PIVOT with Multiple Aggregations
Create a more complex pivot with COUNT and AVG.

```sql
-- Add more test data for better aggregation examples
INSERT INTO #Sales VALUES
('John', 'North', 1100),
('Mary', 'South', 1000),
('Bob', 'East', 1050);

-- COUNT of sales transactions by person and region
SELECT SalesPerson, 
       [North], 
       [South], 
       [East]
FROM (
    SELECT SalesPerson, Region, SalesAmount
    FROM #Sales
) AS SourceTable
PIVOT (
    COUNT(SalesAmount)
    FOR Region IN ([North], [South], [East])
) AS PivotTable;
```

**Result:**
```
SalesPerson | North | South | East
------------|-------|-------|------
Bob         | 1     | 1     | 2
John        | 2     | 1     | 1
Mary        | 1     | 2     | 1
```

### Example 3: Dynamic PIVOT
When you don't know the column values in advance.

```sql
DECLARE @cols NVARCHAR(MAX) = '';
DECLARE @query NVARCHAR(MAX) = '';

-- Build the column list dynamically
SELECT @cols = @cols + QUOTENAME(Region) + ','
FROM (SELECT DISTINCT Region FROM #Sales) AS Regions;

-- Remove trailing comma
SET @cols = LEFT(@cols, LEN(@cols) - 1);

-- Build the dynamic query
SET @query = 'SELECT SalesPerson, ' + @cols + '
FROM (
    SELECT SalesPerson, Region, SalesAmount
    FROM #Sales
) AS SourceTable
PIVOT (
    SUM(SalesAmount)
    FOR Region IN (' + @cols + ')
) AS PivotTable';

EXEC sp_executesql @query;
```

---

## UNPIVOT Examples

### Test Data Setup for UNPIVOT
```sql
-- Create pivoted sales data
CREATE TABLE #SalesPivoted (
    SalesPerson VARCHAR(50),
    North DECIMAL(10,2),
    South DECIMAL(10,2),
    East DECIMAL(10,2)
);

INSERT INTO #SalesPivoted VALUES
('John', 2100, 1500, 800),
('Mary', 1200, 1900, 1100),
('Bob', 800, 1300, 2000);
```

### Example 1: Basic UNPIVOT
Transform columns back to rows.

```sql
SELECT SalesPerson, 
       Region, 
       SalesAmount
FROM (
    SELECT SalesPerson, North, South, East
    FROM #SalesPivoted
) AS SourceTable
UNPIVOT (
    SalesAmount FOR Region IN (North, South, East)
) AS UnpivotTable;
```

**Result:**
```
SalesPerson | Region | SalesAmount
------------|--------|------------
John        | North  | 2100
John        | South  | 1500
John        | East   | 800
Mary        | North  | 1200
Mary        | South  | 1900
Mary        | East   | 1100
Bob         | North  | 800
Bob         | South  | 1300
Bob         | East   | 2000
```

### Example 2: UNPIVOT with Filtering
UNPIVOT and filter results in the same query.

```sql
SELECT SalesPerson, 
       Region, 
       SalesAmount
FROM (
    SELECT SalesPerson, North, South, East
    FROM #SalesPivoted
) AS SourceTable
UNPIVOT (
    SalesAmount FOR Region IN (North, South, East)
) AS UnpivotTable
WHERE SalesAmount > 1000;
```

**Result:**
```
SalesPerson | Region | SalesAmount
------------|--------|------------
John        | North  | 2100
John        | South  | 1500
Mary        | North  | 1200
Mary        | South  | 1900
Mary        | East   | 1100
Bob         | South  | 1300
Bob         | East   | 2000
```

---

## Common Pitfalls and Tips

### PIVOT Tips
1. **Column names must be known**: PIVOT requires literal values in the IN clause
2. **NULL handling**: PIVOT ignores NULL values in aggregations
3. **Data types**: All pivoted columns will have the same data type as the aggregated column
4. **Performance**: Consider indexing on the FOR column for better performance

### UNPIVOT Tips
1. **NULL values**: UNPIVOT excludes rows where the value is NULL
2. **Data type consistency**: All unpivoted columns must have compatible data types
3. **Column aliases**: Use meaningful aliases for the values and names columns

### Performance Considerations
- **PIVOT**: Use indexes on grouping columns and the FOR column
- **UNPIVOT**: Consider using UNION ALL instead of UNPIVOT for better performance with large datasets
- **Dynamic PIVOT**: Cache dynamic SQL when possible to avoid repeated compilation

### Alternative Methods
```sql
-- Alternative to PIVOT using CASE statements
SELECT SalesPerson,
       SUM(CASE WHEN Region = 'North' THEN SalesAmount END) AS North,
       SUM(CASE WHEN Region = 'South' THEN SalesAmount END) AS South,
       SUM(CASE WHEN Region = 'East' THEN SalesAmount END) AS East
FROM #Sales
GROUP BY SalesPerson;

-- Alternative to UNPIVOT using UNION ALL
SELECT SalesPerson, 'North' as Region, North as SalesAmount FROM #SalesPivoted
UNION ALL
SELECT SalesPerson, 'South' as Region, South as SalesAmount FROM #SalesPivoted
UNION ALL
SELECT SalesPerson, 'East' as Region, East as SalesAmount FROM #SalesPivoted;
```

---

## Cleanup
```sql
-- Clean up temporary tables
DROP TABLE #Sales;
DROP TABLE #SalesPivoted;
```
