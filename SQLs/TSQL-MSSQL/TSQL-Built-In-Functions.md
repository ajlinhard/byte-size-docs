# T-SQL Built-In Functions
This is a comprehensive cheatsheet of MSSQL built-in functions organized by data type. This will be a useful reference document for database operations.I've created a comprehensive cheatsheet of MSSQL built-in functions organized by data type. The cheatsheet includes:

- **String Functions** - for text manipulation (LEN, SUBSTRING, REPLACE, etc.)
- **Numeric Functions** - for mathematical operations (ABS, ROUND, POWER, etc.)
- **Date/Time Functions** - for date operations (GETDATE, DATEDIFF, DATEADD, etc.)
- **Conversion Functions** - for data type conversions (CAST, CONVERT, TRY_CAST, etc.)
- **NULL Handling Functions** - for dealing with NULL values (ISNULL, COALESCE, etc.)
- **Aggregate Functions** - for summarizing data (COUNT, SUM, AVG, etc.)
- **Window Functions** - for advanced analytics (ROW_NUMBER, RANK, LAG, etc.)
- **System Functions** - for system information (NEWID, USER_NAME, etc.)
- **JSON Functions** - for JSON data manipulation (available in SQL Server 2016+)

Each function includes its purpose, type (scalar, aggregate, window, or table), and a concise example showing how to use it. This should serve as a quick reference for database operations across different data types in MSSQL.

---
# MSSQL Built-in Functions Cheatsheet

## String Functions

| Function Name | Purpose | Type | Example |
|---------------|---------|------|---------|
| LEN | Returns string length | Scalar | `SELECT LEN('Hello')` → 5 |
| LEFT | Returns leftmost characters | Scalar | `SELECT LEFT('Hello', 3)` → 'Hel' |
| RIGHT | Returns rightmost characters | Scalar | `SELECT RIGHT('Hello', 3)` → 'llo' |
| SUBSTRING | Extracts substring | Scalar | `SELECT SUBSTRING('Hello', 2, 3)` → 'ell' |
| UPPER | Converts to uppercase | Scalar | `SELECT UPPER('hello')` → 'HELLO' |
| LOWER | Converts to lowercase | Scalar | `SELECT LOWER('HELLO')` → 'hello' |
| LTRIM | Removes leading spaces | Scalar | `SELECT LTRIM('  text')` → 'text' |
| RTRIM | Removes trailing spaces | Scalar | `SELECT RTRIM('text  ')` → 'text' |
| TRIM | Removes leading/trailing spaces | Scalar | `SELECT TRIM('  text  ')` → 'text' |
| REPLACE | Replaces substring | Scalar | `SELECT REPLACE('Hello', 'l', 'x')` → 'Hexxo' |
| CHARINDEX | Finds position of substring | Scalar | `SELECT CHARINDEX('ll', 'Hello')` → 3 |
| PATINDEX | Finds pattern position | Scalar | `SELECT PATINDEX('%[0-9]%', 'abc123')` → 4 |
| CONCAT | Concatenates strings | Scalar | `SELECT CONCAT('Hello', ' World')` → 'Hello World' |
| STUFF | Replaces characters at position | Scalar | `SELECT STUFF('Hello', 2, 2, 'i')` → 'Hilo' |
| REVERSE | Reverses string | Scalar | `SELECT REVERSE('Hello')` → 'olleH' |
| REPLICATE | Repeats string | Scalar | `SELECT REPLICATE('Hi', 3)` → 'HiHiHi' |
| SPACE | Returns spaces | Scalar | `SELECT 'A' + SPACE(3) + 'B'` → 'A   B' |
| STRING_SPLIT | Splits string into rows | Table | `SELECT * FROM STRING_SPLIT('a,b,c', ',')` |

## Numeric Functions

| Function Name | Purpose | Type | Example |
|---------------|---------|------|---------|
| ABS | Absolute value | Scalar | `SELECT ABS(-5)` → 5 |
| CEILING | Smallest integer ≥ value | Scalar | `SELECT CEILING(4.2)` → 5 |
| FLOOR | Largest integer ≤ value | Scalar | `SELECT FLOOR(4.8)` → 4 |
| ROUND | Rounds to specified decimal places | Scalar | `SELECT ROUND(4.567, 2)` → 4.57 |
| POWER | Raises to power | Scalar | `SELECT POWER(2, 3)` → 8 |
| SQRT | Square root | Scalar | `SELECT SQRT(16)` → 4 |
| EXP | e raised to power | Scalar | `SELECT EXP(1)` → 2.718... |
| LOG | Natural logarithm | Scalar | `SELECT LOG(10)` → 2.302... |
| LOG10 | Base-10 logarithm | Scalar | `SELECT LOG10(100)` → 2 |
| SIN | Sine (radians) | Scalar | `SELECT SIN(PI()/2)` → 1 |
| COS | Cosine (radians) | Scalar | `SELECT COS(PI())` → -1 |
| TAN | Tangent (radians) | Scalar | `SELECT TAN(PI()/4)` → 1 |
| PI | Returns π | Scalar | `SELECT PI()` → 3.141... |
| RAND | Random number 0-1 | Scalar | `SELECT RAND()` → 0.234... |
| SIGN | Returns sign (-1, 0, 1) | Scalar | `SELECT SIGN(-5)` → -1 |
| DEGREES | Converts radians to degrees | Scalar | `SELECT DEGREES(PI())` → 180 |
| RADIANS | Converts degrees to radians | Scalar | `SELECT RADIANS(180)` → 3.141... |

## Date/Time Functions

| Function Name | Purpose | Type | Example |
|---------------|---------|------|---------|
| GETDATE | Current date/time | Scalar | `SELECT GETDATE()` → 2024-01-15 10:30:00 |
| GETUTCDATE | Current UTC date/time | Scalar | `SELECT GETUTCDATE()` → 2024-01-15 15:30:00 |
| SYSDATETIME | Current date/time (higher precision) | Scalar | `SELECT SYSDATETIME()` |
| DATEPART | Extracts part of date | Scalar | `SELECT DATEPART(year, '2024-01-15')` → 2024 |
| YEAR | Extracts year | Scalar | `SELECT YEAR('2024-01-15')` → 2024 |
| MONTH | Extracts month | Scalar | `SELECT MONTH('2024-01-15')` → 1 |
| DAY | Extracts day | Scalar | `SELECT DAY('2024-01-15')` → 15 |
| DATENAME | Returns date part name | Scalar | `SELECT DATENAME(month, '2024-01-15')` → 'January' |
| DATEDIFF | Difference between dates | Scalar | `SELECT DATEDIFF(day, '2024-01-01', '2024-01-15')` → 14 |
| DATEADD | Adds interval to date | Scalar | `SELECT DATEADD(day, 7, '2024-01-15')` → 2024-01-22 |
| EOMONTH | End of month | Scalar | `SELECT EOMONTH('2024-01-15')` → 2024-01-31 |
| DATEFROMPARTS | Creates date from parts | Scalar | `SELECT DATEFROMPARTS(2024, 1, 15)` → 2024-01-15 |
| ISDATE | Checks if valid date | Scalar | `SELECT ISDATE('2024-01-15')` → 1 |
| FORMAT | Formats date/time | Scalar | `SELECT FORMAT(GETDATE(), 'yyyy-MM-dd')` |

## Conversion Functions

| Function Name | Purpose | Type | Example |
|---------------|---------|------|---------|
| CAST | Converts data type | Scalar | `SELECT CAST('123' AS INT)` → 123 |
| CONVERT | Converts with style options | Scalar | `SELECT CONVERT(VARCHAR, GETDATE(), 101)` → '01/15/2024' |
| TRY_CAST | Safe conversion (returns NULL on error) | Scalar | `SELECT TRY_CAST('abc' AS INT)` → NULL |
| TRY_CONVERT | Safe conversion with style | Scalar | `SELECT TRY_CONVERT(INT, 'abc')` → NULL |
| PARSE | Converts string to data type | Scalar | `SELECT PARSE('123' AS INT)` → 123 |
| TRY_PARSE | Safe parsing | Scalar | `SELECT TRY_PARSE('abc' AS INT)` → NULL |
| STR | Converts number to string | Scalar | `SELECT STR(123.45, 6, 2)` → '123.45' |
| ISNUMERIC | Checks if numeric | Scalar | `SELECT ISNUMERIC('123')` → 1 |

## NULL Handling Functions

| Function Name | Purpose | Type | Example |
|---------------|---------|------|---------|
| ISNULL | Replaces NULL with value | Scalar | `SELECT ISNULL(NULL, 'default')` → 'default' |
| COALESCE | Returns first non-NULL value | Scalar | `SELECT COALESCE(NULL, NULL, 'value')` → 'value' |
| NULLIF | Returns NULL if values equal | Scalar | `SELECT NULLIF(5, 5)` → NULL |
| IIF | Conditional expression | Scalar | `SELECT IIF(1=1, 'true', 'false')` → 'true' |

## Aggregate Functions

| Function Name | Purpose | Type | Example |
|---------------|---------|------|---------|
| COUNT | Counts rows | Aggregate | `SELECT COUNT(*) FROM table` |
| SUM | Sums values | Aggregate | `SELECT SUM(price) FROM products` |
| AVG | Average value | Aggregate | `SELECT AVG(salary) FROM employees` |
| MIN | Minimum value | Aggregate | `SELECT MIN(age) FROM customers` |
| MAX | Maximum value | Aggregate | `SELECT MAX(score) FROM tests` |
| STDEV | Standard deviation | Aggregate | `SELECT STDEV(salary) FROM employees` |
| VAR | Variance | Aggregate | `SELECT VAR(price) FROM products` |
| STRING_AGG | Concatenates strings | Aggregate | `SELECT STRING_AGG(name, ', ') FROM users` |

## Window Functions

| Function Name | Purpose | Type | Example |
|---------------|---------|------|---------|
| ROW_NUMBER | Sequential row numbers | Window | `SELECT ROW_NUMBER() OVER (ORDER BY id)` |
| RANK | Rank with gaps | Window | `SELECT RANK() OVER (ORDER BY score DESC)` |
| DENSE_RANK | Rank without gaps | Window | `SELECT DENSE_RANK() OVER (ORDER BY score DESC)` |
| NTILE | Divides into buckets | Window | `SELECT NTILE(4) OVER (ORDER BY salary)` |
| LAG | Previous row value | Window | `SELECT LAG(price, 1) OVER (ORDER BY date)` |
| LEAD | Next row value | Window | `SELECT LEAD(price, 1) OVER (ORDER BY date)` |
| FIRST_VALUE | First value in window | Window | `SELECT FIRST_VALUE(price) OVER (ORDER BY date)` |
| LAST_VALUE | Last value in window | Window | `SELECT LAST_VALUE(price) OVER (ORDER BY date)` |

## System Functions

| Function Name | Purpose | Type | Example |
|---------------|---------|------|---------|
| NEWID | Generates unique identifier | Scalar | `SELECT NEWID()` → 'A1B2C3D4-...' |
| USER_NAME | Current user name | Scalar | `SELECT USER_NAME()` → 'sa' |
| SYSTEM_USER | System user name | Scalar | `SELECT SYSTEM_USER` → 'DOMAIN\user' |
| HOST_NAME | Host computer name | Scalar | `SELECT HOST_NAME()` → 'SERVER01' |
| DB_NAME | Current database name | Scalar | `SELECT DB_NAME()` → 'MyDatabase' |
| OBJECT_ID | Object ID from name | Scalar | `SELECT OBJECT_ID('Users')` → 245575913 |
| OBJECT_NAME | Object name from ID | Scalar | `SELECT OBJECT_NAME(245575913)` → 'Users' |
| @@IDENTITY | Last identity value | Scalar | `SELECT @@IDENTITY` → 1001 |
| @@ROWCOUNT | Rows affected by last statement | Scalar | `SELECT @@ROWCOUNT` → 5 |

## JSON Functions (SQL Server 2016+)

| Function Name | Purpose | Type | Example |
|---------------|---------|------|---------|
| JSON_VALUE | Extracts scalar value from JSON | Scalar | `SELECT JSON_VALUE('{"name":"John"}', '$.name')` → 'John' |
| JSON_QUERY | Extracts object/array from JSON | Scalar | `SELECT JSON_QUERY('{"items":[1,2]}', '$.items')` → '[1,2]' |
| JSON_MODIFY | Modifies JSON | Scalar | `SELECT JSON_MODIFY('{"name":"John"}', '$.age', 30)` |
| ISJSON | Checks if valid JSON | Scalar | `SELECT ISJSON('{"name":"John"}')` → 1 |
| OPENJSON | Parses JSON into table | Table | `SELECT * FROM OPENJSON('{"name":"John"}')` |

## Notes

- **Scalar Functions**: Return single value, can be used in SELECT, WHERE, ORDER BY
- **Aggregate Functions**: Operate on sets of rows, used with GROUP BY
- **Window Functions**: Perform calculations across related rows
- **Table Functions**: Return table results

Remember to check SQL Server version compatibility for newer functions like JSON functions and some string functions.
