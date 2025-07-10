# Spark SQL Function Cheatsheet
Below is a comprehensive Spark SQL functions cheatsheet! The updated version now includes:

**Key Features Added:**
- **Lateral View Column**: Shows "Required", "Optional", or "No" for each function
- **Additional Function Categories**: Hash functions, bitwise operations, miscellaneous functions, data generation, and URL/URI functions
- **Lateral View Examples**: Comprehensive examples showing required vs optional usage
- **Advanced SQL Patterns**: Real-world examples combining multiple functions
- **Performance Notes**: Guidance on when LATERAL VIEW is needed and performance considerations

**Lateral View Usage:**
- **Required**: For `EXPLODE`, `POSEXPLODE`, `JSON_TUPLE`, `INLINE` and their OUTER variants
- **Optional**: For functions like `WINDOW` when you need complex processing
- **No**: For most scalar functions that operate on single values

**Notable Additions:**
- Complete coverage of all major Spark SQL function categories
- Examples showing multiple LATERAL VIEW clauses in one query
- OUTER variants for handling null/empty collections
- Complex real-world SQL patterns combining multiple functions
- Performance considerations for different function types

The cheatsheet now serves as a complete reference for Spark SQL functions with clear guidance on when LATERAL VIEW syntax is required versus optional, making it much easier to write correct SQL queries in Spark.

---
# Spark SQL Functions Cheatsheet by Data Type

## String Functions

| Function | Purpose | Parameters | Lateral View | Example |
|----------|---------|------------|--------------|---------|
| `LENGTH()` | Get string length | `str` | No | `SELECT LENGTH(name) FROM table` |
| `UPPER()` | Convert to uppercase | `str` | No | `SELECT UPPER(name) FROM table` |
| `LOWER()` | Convert to lowercase | `str` | No | `SELECT LOWER(name) FROM table` |
| `TRIM()` | Remove leading/trailing spaces | `str` | No | `SELECT TRIM(name) FROM table` |
| `LTRIM()` | Remove leading spaces | `str` | No | `SELECT LTRIM(name) FROM table` |
| `RTRIM()` | Remove trailing spaces | `str` | No | `SELECT RTRIM(name) FROM table` |
| `SUBSTRING()` | Extract substring | `str, pos, len` | No | `SELECT SUBSTRING(name, 1, 3) FROM table` |
| `SUBSTR()` | Extract substring (alias) | `str, pos, len` | No | `SELECT SUBSTR(name, 1, 3) FROM table` |
| `SPLIT()` | Split string by delimiter | `str, pattern, limit` | No | `SELECT SPLIT(name, ' ') FROM table` |
| `CONCAT()` | Concatenate strings | `str1, str2, ...` | No | `SELECT CONCAT(first_name, last_name) FROM table` |
| `CONCAT_WS()` | Concatenate with separator | `sep, str1, str2, ...` | No | `SELECT CONCAT_WS(' ', first_name, last_name) FROM table` |
| `REGEXP_REPLACE()` | Replace using regex | `str, pattern, replacement` | No | `SELECT REGEXP_REPLACE(name, 'a', 'b') FROM table` |
| `REGEXP_EXTRACT()` | Extract using regex | `str, pattern, idx` | No | `SELECT REGEXP_EXTRACT(email, '@(.+)', 1) FROM table` |
| `LIKE` | SQL LIKE pattern matching | `str LIKE pattern` | No | `SELECT * FROM table WHERE name LIKE '%John%'` |
| `RLIKE` | Regex pattern matching | `str RLIKE pattern` | No | `SELECT * FROM table WHERE name RLIKE '^A.*'` |
| `INSTR()` | Find position of substring | `str, substr` | No | `SELECT INSTR(name, 'a') FROM table` |
| `LOCATE()` | Find position of substring | `substr, str, pos` | No | `SELECT LOCATE('a', name) FROM table` |
| `LPAD()` | Left pad with characters | `str, len, pad` | No | `SELECT LPAD(id, 5, '0') FROM table` |
| `RPAD()` | Right pad with characters | `str, len, pad` | No | `SELECT RPAD(id, 5, '0') FROM table` |
| `REVERSE()` | Reverse string | `str` | No | `SELECT REVERSE(name) FROM table` |
| `REPEAT()` | Repeat string n times | `str, n` | No | `SELECT REPEAT(char_col, 3) FROM table` |
| `TRANSLATE()` | Replace characters | `str, from, to` | No | `SELECT TRANSLATE(name, 'aei', 'xyz') FROM table` |
| `INITCAP()` | Title case | `str` | No | `SELECT INITCAP(name) FROM table` |
| `SOUNDEX()` | Soundex encoding | `str` | No | `SELECT SOUNDEX(name) FROM table` |
| `LEVENSHTEIN()` | Edit distance | `str1, str2` | No | `SELECT LEVENSHTEIN(name1, name2) FROM table` |
| `ASCII()` | ASCII value of first char | `str` | No | `SELECT ASCII(name) FROM table` |
| `CHR()` | Character from ASCII | `int` | No | `SELECT CHR(65) FROM table` |
| `ENCODE()` | Encode string | `str, charset` | No | `SELECT ENCODE(name, 'UTF-8') FROM table` |
| `DECODE()` | Decode binary | `bin, charset` | No | `SELECT DECODE(binary_col, 'UTF-8') FROM table` |

## Numeric Functions

| Function | Purpose | Parameters | Lateral View | Example |
|----------|---------|------------|--------------|---------|
| `ABS()` | Absolute value | `num` | No | `SELECT ABS(value) FROM table` |
| `CEIL()` | Ceiling | `num` | No | `SELECT CEIL(value) FROM table` |
| `CEILING()` | Ceiling (alias) | `num` | No | `SELECT CEILING(value) FROM table` |
| `FLOOR()` | Floor | `num` | No | `SELECT FLOOR(value) FROM table` |
| `ROUND()` | Round to n decimal places | `num, scale` | No | `SELECT ROUND(value, 2) FROM table` |
| `SQRT()` | Square root | `num` | No | `SELECT SQRT(value) FROM table` |
| `POW()` | Power | `base, exp` | No | `SELECT POW(base, exp) FROM table` |
| `POWER()` | Power (alias) | `base, exp` | No | `SELECT POWER(base, exp) FROM table` |
| `EXP()` | Exponential | `num` | No | `SELECT EXP(value) FROM table` |
| `LN()` | Natural logarithm | `num` | No | `SELECT LN(value) FROM table` |
| `LOG()` | Natural logarithm | `num` | No | `SELECT LOG(value) FROM table` |
| `LOG10()` | Base-10 logarithm | `num` | No | `SELECT LOG10(value) FROM table` |
| `LOG2()` | Base-2 logarithm | `num` | No | `SELECT LOG2(value) FROM table` |
| `SIN()` | Sine | `num` | No | `SELECT SIN(angle) FROM table` |
| `COS()` | Cosine | `num` | No | `SELECT COS(angle) FROM table` |
| `TAN()` | Tangent | `num` | No | `SELECT TAN(angle) FROM table` |
| `ASIN()` | Arc sine | `num` | No | `SELECT ASIN(value) FROM table` |
| `ACOS()` | Arc cosine | `num` | No | `SELECT ACOS(value) FROM table` |
| `ATAN()` | Arc tangent | `num` | No | `SELECT ATAN(value) FROM table` |
| `ATAN2()` | Arc tangent of y/x | `y, x` | No | `SELECT ATAN2(y, x) FROM table` |
| `DEGREES()` | Convert radians to degrees | `num` | No | `SELECT DEGREES(radians) FROM table` |
| `RADIANS()` | Convert degrees to radians | `num` | No | `SELECT RADIANS(degrees) FROM table` |
| `SIGN()` | Sign function | `num` | No | `SELECT SIGN(value) FROM table` |
| `SIGNUM()` | Sign function (alias) | `num` | No | `SELECT SIGNUM(value) FROM table` |
| `GREATEST()` | Maximum of values | `val1, val2, ...` | No | `SELECT GREATEST(a, b, c) FROM table` |
| `LEAST()` | Minimum of values | `val1, val2, ...` | No | `SELECT LEAST(a, b, c) FROM table` |
| `ISNAN()` | Check if NaN | `num` | No | `SELECT * FROM table WHERE ISNAN(value)` |
| `RAND()` | Random number | `seed` | No | `SELECT RAND(42) FROM table` |
| `RANDN()` | Random normal | `seed` | No | `SELECT RANDN(42) FROM table` |
| `BIN()` | Binary representation | `num` | No | `SELECT BIN(value) FROM table` |
| `HEX()` | Hexadecimal representation | `num` | No | `SELECT HEX(value) FROM table` |
| `UNHEX()` | Unhexadecimal | `str` | No | `SELECT UNHEX(hex_value) FROM table` |
| `CONV()` | Base conversion | `num, from_base, to_base` | No | `SELECT CONV(value, 10, 16) FROM table` |
| `BROUND()` | Banker's rounding | `num, scale` | No | `SELECT BROUND(value, 2) FROM table` |
| `SHIFTLEFT()` | Bitwise left shift | `num, positions` | No | `SELECT SHIFTLEFT(value, 2) FROM table` |
| `SHIFTRIGHT()` | Bitwise right shift | `num, positions` | No | `SELECT SHIFTRIGHT(value, 2) FROM table` |
| `SHIFTRIGHTUNSIGNED()` | Unsigned right shift | `num, positions` | No | `SELECT SHIFTRIGHTUNSIGNED(value, 2) FROM table` |

## Date/Time Functions

| Function | Purpose | Parameters | Lateral View | Example |
|----------|---------|------------|--------------|---------|
| `CURRENT_DATE()` | Current date | - | No | `SELECT CURRENT_DATE()` |
| `CURRENT_TIMESTAMP()` | Current timestamp | - | No | `SELECT CURRENT_TIMESTAMP()` |
| `NOW()` | Current timestamp (alias) | - | No | `SELECT NOW()` |
| `DATE_FORMAT()` | Format date | `date, format` | No | `SELECT DATE_FORMAT(date_col, 'yyyy-MM-dd') FROM table` |
| `TO_DATE()` | Convert to date | `str, format` | No | `SELECT TO_DATE(date_str, 'yyyy-MM-dd') FROM table` |
| `TO_TIMESTAMP()` | Convert to timestamp | `str, format` | No | `SELECT TO_TIMESTAMP(ts_str, 'yyyy-MM-dd HH:mm:ss') FROM table` |
| `YEAR()` | Extract year | `date` | No | `SELECT YEAR(date_col) FROM table` |
| `MONTH()` | Extract month | `date` | No | `SELECT MONTH(date_col) FROM table` |
| `DAY()` | Extract day of month | `date` | No | `SELECT DAY(date_col) FROM table` |
| `DAYOFMONTH()` | Extract day of month | `date` | No | `SELECT DAYOFMONTH(date_col) FROM table` |
| `DAYOFWEEK()` | Extract day of week | `date` | No | `SELECT DAYOFWEEK(date_col) FROM table` |
| `DAYOFYEAR()` | Extract day of year | `date` | No | `SELECT DAYOFYEAR(date_col) FROM table` |
| `HOUR()` | Extract hour | `timestamp` | No | `SELECT HOUR(timestamp_col) FROM table` |
| `MINUTE()` | Extract minute | `timestamp` | No | `SELECT MINUTE(timestamp_col) FROM table` |
| `SECOND()` | Extract second | `timestamp` | No | `SELECT SECOND(timestamp_col) FROM table` |
| `WEEKOFYEAR()` | Extract week of year | `date` | No | `SELECT WEEKOFYEAR(date_col) FROM table` |
| `QUARTER()` | Extract quarter | `date` | No | `SELECT QUARTER(date_col) FROM table` |
| `DATE_ADD()` | Add days to date | `date, days` | No | `SELECT DATE_ADD(date_col, 30) FROM table` |
| `DATE_SUB()` | Subtract days from date | `date, days` | No | `SELECT DATE_SUB(date_col, 30) FROM table` |
| `DATEDIFF()` | Days between dates | `end_date, start_date` | No | `SELECT DATEDIFF(end_date, start_date) FROM table` |
| `MONTHS_BETWEEN()` | Months between dates | `end_date, start_date` | No | `SELECT MONTHS_BETWEEN(end_date, start_date) FROM table` |
| `ADD_MONTHS()` | Add months to date | `date, months` | No | `SELECT ADD_MONTHS(date_col, 3) FROM table` |
| `NEXT_DAY()` | Next occurrence of weekday | `date, day_of_week` | No | `SELECT NEXT_DAY(date_col, 'Monday') FROM table` |
| `LAST_DAY()` | Last day of month | `date` | No | `SELECT LAST_DAY(date_col) FROM table` |
| `TRUNC()` | Truncate date | `date, format` | No | `SELECT TRUNC(date_col, 'month') FROM table` |
| `DATE_TRUNC()` | Truncate timestamp | `format, timestamp` | No | `SELECT DATE_TRUNC('hour', timestamp_col) FROM table` |
| `FROM_UNIXTIME()` | Unix timestamp to string | `unix_time, format` | No | `SELECT FROM_UNIXTIME(unix_time) FROM table` |
| `UNIX_TIMESTAMP()` | String to unix timestamp | `time_str, format` | No | `SELECT UNIX_TIMESTAMP(time_str) FROM table` |
| `FROM_UTC_TIMESTAMP()` | UTC to timezone | `timestamp, timezone` | No | `SELECT FROM_UTC_TIMESTAMP(utc_ts, 'PST') FROM table` |
| `TO_UTC_TIMESTAMP()` | Timezone to UTC | `timestamp, timezone` | No | `SELECT TO_UTC_TIMESTAMP(local_ts, 'PST') FROM table` |
| `WINDOW()` | Time window | `time_col, duration` | Optional | `SELECT WINDOW(timestamp_col, '10 minutes') FROM table` |

## Array Functions

| Function | Purpose | Parameters | Lateral View | Example |
|----------|---------|------------|--------------|---------|
| `ARRAY()` | Create array | `val1, val2, ...` | No | `SELECT ARRAY(a, b, c) FROM table` |
| `ARRAY_CONTAINS()` | Check if array contains value | `array, value` | No | `SELECT * FROM table WHERE ARRAY_CONTAINS(arr, 'value')` |
| `ARRAY_DISTINCT()` | Remove duplicates | `array` | No | `SELECT ARRAY_DISTINCT(arr) FROM table` |
| `ARRAY_EXCEPT()` | Array difference | `array1, array2` | No | `SELECT ARRAY_EXCEPT(arr1, arr2) FROM table` |
| `ARRAY_INTERSECT()` | Array intersection | `array1, array2` | No | `SELECT ARRAY_INTERSECT(arr1, arr2) FROM table` |
| `ARRAY_JOIN()` | Join array elements | `array, delimiter` | No | `SELECT ARRAY_JOIN(arr, ',') FROM table` |
| `ARRAY_MAX()` | Maximum value in array | `array` | No | `SELECT ARRAY_MAX(arr) FROM table` |
| `ARRAY_MIN()` | Minimum value in array | `array` | No | `SELECT ARRAY_MIN(arr) FROM table` |
| `ARRAY_POSITION()` | Find position of element | `array, element` | No | `SELECT ARRAY_POSITION(arr, 'value') FROM table` |
| `ARRAY_REMOVE()` | Remove all occurrences | `array, element` | No | `SELECT ARRAY_REMOVE(arr, 'value') FROM table` |
| `ARRAY_REPEAT()` | Repeat element n times | `element, count` | No | `SELECT ARRAY_REPEAT(value, 3) FROM table` |
| `ARRAY_SORT()` | Sort array | `array` | No | `SELECT ARRAY_SORT(arr) FROM table` |
| `ARRAY_UNION()` | Array union | `array1, array2` | No | `SELECT ARRAY_UNION(arr1, arr2) FROM table` |
| `ARRAYS_OVERLAP()` | Check if arrays overlap | `array1, array2` | No | `SELECT * FROM table WHERE ARRAYS_OVERLAP(arr1, arr2)` |
| `ARRAYS_ZIP()` | Zip arrays together | `array1, array2, ...` | No | `SELECT ARRAYS_ZIP(arr1, arr2) FROM table` |
| `ELEMENT_AT()` | Get element at index | `array, index` | No | `SELECT ELEMENT_AT(arr, 1) FROM table` |
| `EXPLODE()` | Explode array to rows | `array` | Required | `SELECT col FROM table LATERAL VIEW EXPLODE(arr) t AS col` |
| `POSEXPLODE()` | Explode with position | `array` | Required | `SELECT pos, col FROM table LATERAL VIEW POSEXPLODE(arr) t AS pos, col` |
| `REVERSE()` | Reverse array | `array` | No | `SELECT REVERSE(arr) FROM table` |
| `SHUFFLE()` | Shuffle array | `array` | No | `SELECT SHUFFLE(arr) FROM table` |
| `SIZE()` | Get array size | `array` | No | `SELECT SIZE(arr) FROM table` |
| `SLICE()` | Get array slice | `array, start, length` | No | `SELECT SLICE(arr, 1, 3) FROM table` |
| `SORT_ARRAY()` | Sort array | `array, asc` | No | `SELECT SORT_ARRAY(arr, false) FROM table` |
| `FLATTEN()` | Flatten nested arrays | `array` | No | `SELECT FLATTEN(nested_arr) FROM table` |
| `SEQUENCE()` | Generate sequence | `start, stop, step` | No | `SELECT SEQUENCE(1, 10, 2) FROM table` |
| `ARRAY_AGG()` | Aggregate into array | `col` | No | `SELECT ARRAY_AGG(value) FROM table GROUP BY group_col` |

## Map Functions

| Function | Purpose | Parameters | Lateral View | Example |
|----------|---------|------------|--------------|---------|
| `MAP()` | Create map | `key1, val1, key2, val2, ...` | No | `SELECT MAP('key1', value1, 'key2', value2) FROM table` |
| `MAP_KEYS()` | Get map keys | `map` | No | `SELECT MAP_KEYS(map_col) FROM table` |
| `MAP_VALUES()` | Get map values | `map` | No | `SELECT MAP_VALUES(map_col) FROM table` |
| `MAP_ENTRIES()` | Get map entries | `map` | No | `SELECT MAP_ENTRIES(map_col) FROM table` |
| `MAP_FROM_ENTRIES()` | Create map from entries | `array_of_structs` | No | `SELECT MAP_FROM_ENTRIES(entries) FROM table` |
| `MAP_FROM_ARRAYS()` | Create map from arrays | `keys_array, values_array` | No | `SELECT MAP_FROM_ARRAYS(keys, values) FROM table` |
| `MAP_CONCAT()` | Concatenate maps | `map1, map2, ...` | No | `SELECT MAP_CONCAT(map1, map2) FROM table` |
| `ELEMENT_AT()` | Get value by key | `map, key` | No | `SELECT ELEMENT_AT(map_col, 'key') FROM table` |
| `SIZE()` | Get map size | `map` | No | `SELECT SIZE(map_col) FROM table` |
| `EXPLODE()` | Explode map to rows | `map` | Required | `SELECT key, value FROM table LATERAL VIEW EXPLODE(map_col) t AS key, value` |
| `POSEXPLODE()` | Explode map with position | `map` | Required | `SELECT pos, key, value FROM table LATERAL VIEW POSEXPLODE(map_col) t AS pos, key, value` |

## JSON Functions

| Function | Purpose | Parameters | Lateral View | Example |
|----------|---------|------------|--------------|---------|
| `FROM_JSON()` | Parse JSON string | `json_str, schema` | No | `SELECT FROM_JSON(json_str, 'STRUCT<name:STRING,age:INT>') FROM table` |
| `TO_JSON()` | Convert to JSON string | `struct_col` | No | `SELECT TO_JSON(struct_col) FROM table` |
| `JSON_TUPLE()` | Extract JSON fields | `json_col, field1, field2, ...` | Required | `SELECT c0, c1 FROM table LATERAL VIEW JSON_TUPLE(json_col, 'field1', 'field2') t AS c0, c1` |
| `GET_JSON_OBJECT()` | Extract JSON object | `json_col, path` | No | `SELECT GET_JSON_OBJECT(json_col, '$.field') FROM table` |
| `SCHEMA_OF_JSON()` | Get JSON schema | `json_string` | No | `SELECT SCHEMA_OF_JSON('{"a":1,"b":"string"}')` |

## Struct Functions

| Function | Purpose | Parameters | Lateral View | Example |
|----------|---------|------------|--------------|---------|
| `STRUCT()` | Create struct | `col1, col2, ...` | No | `SELECT STRUCT(a, b) FROM table` |
| `NAMED_STRUCT()` | Create named struct | `name1, col1, name2, col2, ...` | No | `SELECT NAMED_STRUCT('field1', a, 'field2', b) FROM table` |
| `INLINE()` | Explode struct array | `array_of_structs` | Required | `SELECT * FROM table LATERAL VIEW INLINE(struct_array) t` |

## Null/Conditional Functions

| Function | Purpose | Parameters | Lateral View | Example |
|----------|---------|------------|--------------|---------|
| `ISNULL()` | Check if null | `expr` | No | `SELECT * FROM table WHERE ISNULL(value)` |
| `ISNOTNULL()` | Check if not null | `expr` | No | `SELECT * FROM table WHERE ISNOTNULL(value)` |
| `ISNAN()` | Check if NaN | `expr` | No | `SELECT * FROM table WHERE ISNAN(value)` |
| `COALESCE()` | First non-null value | `expr1, expr2, ...` | No | `SELECT COALESCE(a, b, 'default') FROM table` |
| `CASE WHEN` | Conditional expression | `WHEN condition THEN value` | No | `SELECT CASE WHEN a > 0 THEN 'positive' ELSE 'negative' END FROM table` |
| `IF()` | Simple conditional | `condition, true_value, false_value` | No | `SELECT IF(a > 0, 'positive', 'negative') FROM table` |
| `NANVL()` | Replace NaN with value | `expr1, expr2` | No | `SELECT NANVL(value, 0) FROM table` |
| `NULLIF()` | Return null if equal | `expr1, expr2` | No | `SELECT NULLIF(a, b) FROM table` |
| `NVL()` | Replace null with value | `expr1, expr2` | No | `SELECT NVL(value, 'default') FROM table` |
| `NVL2()` | Replace null/not null | `expr1, expr2, expr3` | No | `SELECT NVL2(a, b, c) FROM table` |
| `IFNULL()` | Replace null with value | `expr1, expr2` | No | `SELECT IFNULL(value, 'default') FROM table` |

## Type Conversion Functions

| Function | Purpose | Parameters | Lateral View | Example |
|----------|---------|------------|--------------|---------|
| `CAST()` | Cast to data type | `expr AS datatype` | No | `SELECT CAST(str_col AS INT) FROM table` |
| `TYPEOF()` | Get data type | `expr` | No | `SELECT TYPEOF(col) FROM table` |
| `BOOLEAN()` | Convert to boolean | `expr` | No | `SELECT BOOLEAN(int_col) FROM table` |
| `TINYINT()` | Convert to tinyint | `expr` | No | `SELECT TINYINT(str_col) FROM table` |
| `SMALLINT()` | Convert to smallint | `expr` | No | `SELECT SMALLINT(str_col) FROM table` |
| `INT()` | Convert to int | `expr` | No | `SELECT INT(str_col) FROM table` |
| `BIGINT()` | Convert to bigint | `expr` | No | `SELECT BIGINT(str_col) FROM table` |
| `FLOAT()` | Convert to float | `expr` | No | `SELECT FLOAT(str_col) FROM table` |
| `DOUBLE()` | Convert to double | `expr` | No | `SELECT DOUBLE(str_col) FROM table` |
| `DECIMAL()` | Convert to decimal | `expr, precision, scale` | No | `SELECT DECIMAL(value, 10, 2) FROM table` |
| `STRING()` | Convert to string | `expr` | No | `SELECT STRING(int_col) FROM table` |
| `BINARY()` | Convert to binary | `expr` | No | `SELECT BINARY(str_col) FROM table` |

## Aggregate Functions

| Function | Purpose | Parameters | Lateral View | Example |
|----------|---------|------------|--------------|---------|
| `SUM()` | Sum of values | `expr` | No | `SELECT SUM(value) FROM table GROUP BY group_col` |
| `AVG()` | Average of values | `expr` | No | `SELECT AVG(value) FROM table GROUP BY group_col` |
| `MEAN()` | Mean of values (alias) | `expr` | No | `SELECT MEAN(value) FROM table GROUP BY group_col` |
| `COUNT()` | Count of values | `expr` | No | `SELECT COUNT(*) FROM table GROUP BY group_col` |
| `COUNT(DISTINCT)` | Count distinct values | `DISTINCT expr` | No | `SELECT COUNT(DISTINCT value) FROM table GROUP BY group_col` |
| `MAX()` | Maximum value | `expr` | No | `SELECT MAX(value) FROM table GROUP BY group_col` |
| `MIN()` | Minimum value | `expr` | No | `SELECT MIN(value) FROM table GROUP BY group_col` |
| `FIRST()` | First value | `expr, ignore_nulls` | No | `SELECT FIRST(value) FROM table GROUP BY group_col` |
| `LAST()` | Last value | `expr, ignore_nulls` | No | `SELECT LAST(value) FROM table GROUP BY group_col` |
| `STDDEV()` | Standard deviation | `expr` | No | `SELECT STDDEV(value) FROM table GROUP BY group_col` |
| `STDDEV_POP()` | Population std dev | `expr` | No | `SELECT STDDEV_POP(value) FROM table GROUP BY group_col` |
| `STDDEV_SAMP()` | Sample std dev | `expr` | No | `SELECT STDDEV_SAMP(value) FROM table GROUP BY group_col` |
| `VARIANCE()` | Variance | `expr` | No | `SELECT VARIANCE(value) FROM table GROUP BY group_col` |
| `VAR_POP()` | Population variance | `expr` | No | `SELECT VAR_POP(value) FROM table GROUP BY group_col` |
| `VAR_SAMP()` | Sample variance | `expr` | No | `SELECT VAR_SAMP(value) FROM table GROUP BY group_col` |
| `COLLECT_LIST()` | Collect values to list | `expr` | No | `SELECT COLLECT_LIST(value) FROM table GROUP BY group_col` |
| `COLLECT_SET()` | Collect values to set | `expr` | No | `SELECT COLLECT_SET(value) FROM table GROUP BY group_col` |
| `SKEWNESS()` | Skewness | `expr` | No | `SELECT SKEWNESS(value) FROM table GROUP BY group_col` |
| `KURTOSIS()` | Kurtosis | `expr` | No | `SELECT KURTOSIS(value) FROM table GROUP BY group_col` |
| `APPROX_COUNT_DISTINCT()` | Approximate count distinct | `expr, rsd` | No | `SELECT APPROX_COUNT_DISTINCT(value) FROM table GROUP BY group_col` |
| `CORR()` | Correlation | `expr1, expr2` | No | `SELECT CORR(col1, col2) FROM table` |
| `COVAR_POP()` | Population covariance | `expr1, expr2` | No | `SELECT COVAR_POP(col1, col2) FROM table` |
| `COVAR_SAMP()` | Sample covariance | `expr1, expr2` | No | `SELECT COVAR_SAMP(col1, col2) FROM table` |
| `PERCENTILE()` | Percentile | `expr, percentage` | No | `SELECT PERCENTILE(value, 0.5) FROM table GROUP BY group_col` |
| `PERCENTILE_APPROX()` | Approximate percentile | `expr, percentage, accuracy` | No | `SELECT PERCENTILE_APPROX(value, 0.5) FROM table GROUP BY group_col` |

## Window Functions

| Function | Purpose | Parameters | Lateral View | Example |
|----------|---------|------------|--------------|---------|
| `ROW_NUMBER()` | Row number | - | No | `SELECT ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary) FROM table` |
| `RANK()` | Rank with gaps | - | No | `SELECT RANK() OVER (PARTITION BY dept ORDER BY salary) FROM table` |
| `DENSE_RANK()` | Dense rank | - | No | `SELECT DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary) FROM table` |
| `PERCENT_RANK()` | Percent rank | - | No | `SELECT PERCENT_RANK() OVER (PARTITION BY dept ORDER BY salary) FROM table` |
| `NTILE()` | N-tile | `n` | No | `SELECT NTILE(4) OVER (PARTITION BY dept ORDER BY salary) FROM table` |
| `LAG()` | Previous row value | `expr, offset, default` | No | `SELECT LAG(value, 1) OVER (ORDER BY date) FROM table` |
| `LEAD()` | Next row value | `expr, offset, default` | No | `SELECT LEAD(value, 1) OVER (ORDER BY date) FROM table` |
| `FIRST_VALUE()` | First value in window | `expr, ignore_nulls` | No | `SELECT FIRST_VALUE(value) OVER (PARTITION BY group ORDER BY date) FROM table` |
| `LAST_VALUE()` | Last value in window | `expr, ignore_nulls` | No | `SELECT LAST_VALUE(value) OVER (PARTITION BY group ORDER BY date ROWS UNBOUNDED FOLLOWING) FROM table` |
| `CUME_DIST()` | Cumulative distribution | - | No | `SELECT CUME_DIST() OVER (PARTITION BY dept ORDER BY salary) FROM table` |

## Lateral View Syntax Examples

### Required Lateral View
```sql
-- Exploding arrays
SELECT id, exploded_value 
FROM table 
LATERAL VIEW EXPLODE(array_column) t AS exploded_value;

-- Exploding maps
SELECT id, map_key, map_value 
FROM table 
LATERAL VIEW EXPLODE(map_column) t AS map_key, map_value;

-- JSON tuple extraction
SELECT id, field1, field2 
FROM table 
LATERAL VIEW JSON_TUPLE(json_column, 'field1', 'field2') t AS field1, field2;

-- Inline struct arrays
SELECT id, struct_field1, struct_field2 
FROM table 
LATERAL VIEW INLINE(struct_array_column) t;
```

### Optional Lateral View
```sql
-- Can use with or without LATERAL VIEW
SELECT WINDOW(timestamp_col, '10 minutes') FROM table;

-- Or with LATERAL VIEW for more complex processing
SELECT window_start, window_end, COUNT(*) 
FROM table 
LATERAL VIEW EXPLODE(ARRAY(WINDOW(timestamp_col, '10 minutes'))) t AS window_info
GROUP BY window_start, window_end;
```

### Multiple Lateral Views
```sql
-- Multiple LATERAL VIEW clauses in same query
SELECT id, arr_item, map_key, map_value
FROM table 
LATERAL VIEW EXPLODE(array_column) t1 AS arr_item
LATERAL VIEW EXPLODE(map_column) t2 AS map_key, map_value;
```

### Outer Lateral View
```sql
-- Preserves rows even if array/map is empty or null
SELECT id, exploded_value 
FROM table 
LATERAL VIEW OUTER EXPLODE(array_column) t AS exploded_value;
```

## Hash Functions

| Function | Purpose | Parameters | Lateral View | Example |
|----------|---------|------------|--------------|---------|
| `HASH()` | Hash function | `expr1, expr2, ...` | No | `SELECT HASH(col1, col2) FROM table` |
| `MD5()` | MD5 hash | `expr` | No | `SELECT MD5(column) FROM table` |
| `SHA1()` | SHA1 hash | `expr` | No | `SELECT SHA1(column) FROM table` |
| `SHA2()` | SHA2 hash | `expr, bitLength` | No | `SELECT SHA2(column, 256) FROM table` |
| `CRC32()` | CRC32 checksum | `expr` | No | `SELECT CRC32(column) FROM table` |
| `XXHASH64()` | xxHash64 | `expr1, expr2, ...` | No | `SELECT XXHASH64(col1, col2) FROM table` |

## Bitwise Functions

| Function | Purpose | Parameters | Lateral View | Example |
|----------|---------|------------|--------------|---------|
| `&` | Bitwise AND | `expr1 & expr2` | No | `SELECT col1 & col2 FROM table` |
| `|` | Bitwise OR | `expr1 | expr2` | No | `SELECT col1 | col2 FROM table` |
| `^` | Bitwise XOR | `expr1 ^ expr2` | No | `SELECT col1 ^ col2 FROM table` |
| `~` | Bitwise NOT | `~expr` | No | `SELECT ~col1 FROM table` |
| `SHIFTLEFT()` | Left shift | `expr, positions` | No | `SELECT SHIFTLEFT(col1, 2) FROM table` |
| `SHIFTRIGHT()` | Right shift | `expr, positions` | No | `SELECT SHIFTRIGHT(col1, 2) FROM table` |
| `SHIFTRIGHTUNSIGNED()` | Unsigned right shift | `expr, positions` | No | `SELECT SHIFTRIGHTUNSIGNED(col1, 2) FROM table` |

## Miscellaneous Functions

| Function | Purpose | Parameters | Lateral View | Example |
|----------|---------|------------|--------------|---------|
| `MONOTONICALLY_INCREASING_ID()` | Unique increasing ID | - | No | `SELECT MONOTONICALLY_INCREASING_ID() FROM table` |
| `SPARK_PARTITION_ID()` | Current partition ID | - | No | `SELECT SPARK_PARTITION_ID() FROM table` |
| `INPUT_FILE_NAME()` | Input file name | - | No | `SELECT INPUT_FILE_NAME() FROM table` |
| `UUID()` | Generate UUID | - | No | `SELECT UUID() FROM table` |
| `VERSION()` | Spark version | - | No | `SELECT VERSION()` |
| `CURRENT_DATABASE()` | Current database | - | No | `SELECT CURRENT_DATABASE()` |
| `CURRENT_USER()` | Current user | - | No | `SELECT CURRENT_USER()` |
| `STACK()` | Stack columns into rows | `n, expr1, expr2, ...` | No | `SELECT STACK(2, 'a', 1, 'b', 2) AS (col1, col2)` |
| `ASSERT_TRUE()` | Assert condition | `expr, message` | No | `SELECT ASSERT_TRUE(value > 0, 'Value must be positive') FROM table` |
| `RAISE_ERROR()` | Raise error | `message` | No | `SELECT RAISE_ERROR('Custom error message')` |

## Data Generation Functions

| Function | Purpose | Parameters | Lateral View | Example |
|----------|---------|------------|--------------|---------|
| `EXPLODE()` | Generate rows from array | `array` | Required | `SELECT EXPLODE(ARRAY(1, 2, 3)) AS value` |
| `EXPLODE_OUTER()` | Generate rows (keeps nulls) | `array` | Required | `SELECT EXPLODE_OUTER(array_col) FROM table` |
| `POSEXPLODE()` | Generate rows with position | `array` | Required | `SELECT POSEXPLODE(ARRAY(1, 2, 3)) AS (pos, value)` |
| `POSEXPLODE_OUTER()` | Generate rows with pos (keeps nulls) | `array` | Required | `SELECT POSEXPLODE_OUTER(array_col) FROM table` |
| `INLINE()` | Generate rows from struct array | `array_of_structs` | Required | `SELECT INLINE(struct_array) FROM table` |
| `INLINE_OUTER()` | Generate rows (keeps nulls) | `array_of_structs` | Required | `SELECT INLINE_OUTER(struct_array) FROM table` |

## URL/URI Functions

| Function | Purpose | Parameters | Lateral View | Example |
|----------|---------|------------|--------------|---------|
| `PARSE_URL()` | Parse URL component | `url, part, key` | No | `SELECT PARSE_URL('http://example.com/path', 'HOST') FROM table` |
| `JAVA_METHOD()` | Call Java method | `class, method, arg1, ...` | No | `SELECT JAVA_METHOD('java.net.URLDecoder', 'decode', url_col, 'UTF-8') FROM table` |
| `REFLECT()` | Call Java method (alias) | `class, method, arg1, ...` | No | `SELECT REFLECT('java.lang.Math', 'abs', -1)` |

## Common SQL Patterns

### Using LATERAL VIEW with Multiple Functions
```sql
-- Complex array processing
SELECT 
    id,
    array_item,
    SIZE(processed_array) as array_size,
    ARRAY_MAX(processed_array) as max_value
FROM table 
LATERAL VIEW EXPLODE(original_array) t AS array_item
WHERE ARRAY_CONTAINS(original_array, 'specific_value');
```

### Conditional Aggregation
```sql
-- Using CASE in aggregations
SELECT 
    department,
    COUNT(*) as total_employees,
    SUM(CASE WHEN salary > 50000 THEN 1 ELSE 0 END) as high_earners,
    AVG(CASE WHEN age < 30 THEN salary END) as avg_young_salary
FROM employees 
GROUP BY department;
```

### Window Function with Complex Partitioning
```sql
-- Advanced window functions
SELECT 
    employee_id,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as salary_rank,
    LAG(salary, 1) OVER (PARTITION BY department ORDER BY hire_date) as prev_hire_salary,
    SUM(salary) OVER (PARTITION BY department ROWS UNBOUNDED PRECEDING) as running_total
FROM employees;
```

### JSON Processing
```sql
-- Complex JSON extraction
SELECT 
    id,
    GET_JSON_OBJECT(json_data, '$.user.name') as user_name,
    GET_JSON_OBJECT(json_data, '$.user.age') as user_age,
    field1,
    field2
FROM table 
LATERAL VIEW JSON_TUPLE(json_data, 'field1', 'field2') t AS field1, field2;
```

### Array and Map Operations
```sql
-- Combining array and map functions
SELECT 
    id,
    ARRAY_JOIN(MAP_VALUES(user_preferences), ', ') as preferences_list,
    SIZE(ARRAY_INTERSECT(user_tags, popular_tags)) as matching_tags_count
FROM users
WHERE ARRAYS_OVERLAP(user_interests, ARRAY('technology', 'science'));
```

### Date Processing
```sql
-- Complex date calculations
SELECT 
    event_date,
    DAYOFWEEK(event_date) as day_of_week,
    CASE 
        WHEN DAYOFWEEK(event_date) IN (1, 7) THEN 'Weekend'
        ELSE 'Weekday'
    END as day_type,
    DATEDIFF(CURRENT_DATE(), event_date) as days_ago,
    DATE_TRUNC('month', event_date) as month_start
FROM events
WHERE event_date BETWEEN DATE_SUB(CURRENT_DATE(), 30) AND CURRENT_DATE();
```

## Performance Notes

- **LATERAL VIEW**: Required for `EXPLODE`, `POSEXPLODE`, `JSON_TUPLE`, and `INLINE` functions
- **Window Functions**: Can be computationally expensive; consider partitioning strategy
- **Complex Nested Functions**: May benefit from breaking into multiple steps
- **Array Functions**: `EXPLODE` can significantly increase row count; use with caution on large datasets
- **JSON Functions**: `FROM_JSON` with explicit schema is more efficient than `GET_JSON_OBJECT` for multiple fields
