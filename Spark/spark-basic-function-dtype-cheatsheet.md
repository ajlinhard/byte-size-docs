# PySpark Column Functions Cheatsheet by Data Type

## String Functions

| Function | Purpose | Parameters | Example |
|----------|---------|------------|---------|
| `length()` | Get string length | `col` | `df.select(length(col("name")))` |
| `upper()` | Convert to uppercase | `col` | `df.select(upper(col("name")))` |
| `lower()` | Convert to lowercase | `col` | `df.select(lower(col("name")))` |
| `trim()` | Remove leading/trailing spaces | `col` | `df.select(trim(col("name")))` |
| `ltrim()` | Remove leading spaces | `col` | `df.select(ltrim(col("name")))` |
| `rtrim()` | Remove trailing spaces | `col` | `df.select(rtrim(col("name")))` |
| `substring()` | Extract substring | `str, pos, len` | `df.select(substring(col("name"), 1, 3))` |
| `substr()` | Extract substring (alias) | `str, pos, len` | `df.select(substr(col("name"), 1, 3))` |
| `split()` | Split string by delimiter | `str, pattern, limit` | `df.select(split(col("name"), " "))` |
| `concat()` | Concatenate strings | `*cols` | `df.select(concat(col("first"), col("last")))` |
| `concat_ws()` | Concatenate with separator | `sep, *cols` | `df.select(concat_ws(" ", col("first"), col("last")))` |
| `regexp_replace()` | Replace using regex | `str, pattern, replacement` | `df.select(regexp_replace(col("name"), "a", "b"))` |
| `regexp_extract()` | Extract using regex | `str, pattern, idx` | `df.select(regexp_extract(col("email"), r"@(.+)", 1))` |
| `contains()` | Check if contains substring | `other` | `df.filter(col("name").contains("John"))` |
| `startswith()` | Check if starts with | `other` | `df.filter(col("name").startswith("A"))` |
| `endswith()` | Check if ends with | `other` | `df.filter(col("name").endswith("son"))` |
| `like()` | SQL LIKE pattern matching | `other` | `df.filter(col("name").like("%John%"))` |
| `rlike()` | Regex pattern matching | `other` | `df.filter(col("name").rlike("^A.*"))` |
| `instr()` | Find position of substring | `str, substr` | `df.select(instr(col("name"), "a"))` |
| `locate()` | Find position of substring | `substr, str, pos` | `df.select(locate("a", col("name")))` |
| `lpad()` | Left pad with characters | `col, len, pad` | `df.select(lpad(col("id"), 5, "0"))` |
| `rpad()` | Right pad with characters | `col, len, pad` | `df.select(rpad(col("id"), 5, "0"))` |
| `reverse()` | Reverse string | `col` | `df.select(reverse(col("name")))` |
| `repeat()` | Repeat string n times | `col, n` | `df.select(repeat(col("char"), 3))` |
| `translate()` | Replace characters | `srcCol, matching, replace` | `df.select(translate(col("name"), "aei", "xyz"))` |
| `initcap()` | Title case | `col` | `df.select(initcap(col("name")))` |
| `soundex()` | Soundex encoding | `col` | `df.select(soundex(col("name")))` |
| `levenshtein()` | Edit distance | `left, right` | `df.select(levenshtein(col("name1"), col("name2")))` |

## Numeric Functions

| Function | Purpose | Parameters | Example |
|----------|---------|------------|---------|
| `abs()` | Absolute value | `col` | `df.select(abs(col("value")))` |
| `ceil()` | Ceiling | `col` | `df.select(ceil(col("value")))` |
| `floor()` | Floor | `col` | `df.select(floor(col("value")))` |
| `round()` | Round to n decimal places | `col, scale` | `df.select(round(col("value"), 2))` |
| `sqrt()` | Square root | `col` | `df.select(sqrt(col("value")))` |
| `pow()` | Power | `col1, col2` | `df.select(pow(col("base"), col("exp")))` |
| `exp()` | Exponential | `col` | `df.select(exp(col("value")))` |
| `log()` | Natural logarithm | `col` | `df.select(log(col("value")))` |
| `log10()` | Base-10 logarithm | `col` | `df.select(log10(col("value")))` |
| `log2()` | Base-2 logarithm | `col` | `df.select(log2(col("value")))` |
| `sin()` | Sine | `col` | `df.select(sin(col("angle")))` |
| `cos()` | Cosine | `col` | `df.select(cos(col("angle")))` |
| `tan()` | Tangent | `col` | `df.select(tan(col("angle")))` |
| `asin()` | Arc sine | `col` | `df.select(asin(col("value")))` |
| `acos()` | Arc cosine | `col` | `df.select(acos(col("value")))` |
| `atan()` | Arc tangent | `col` | `df.select(atan(col("value")))` |
| `atan2()` | Arc tangent of y/x | `col1, col2` | `df.select(atan2(col("y"), col("x")))` |
| `degrees()` | Convert radians to degrees | `col` | `df.select(degrees(col("radians")))` |
| `radians()` | Convert degrees to radians | `col` | `df.select(radians(col("degrees")))` |
| `signum()` | Sign function | `col` | `df.select(signum(col("value")))` |
| `greatest()` | Maximum of values | `*cols` | `df.select(greatest(col("a"), col("b"), col("c")))` |
| `least()` | Minimum of values | `*cols` | `df.select(least(col("a"), col("b"), col("c")))` |
| `isnan()` | Check if NaN | `col` | `df.filter(isnan(col("value")))` |
| `isinf()` | Check if infinite | `col` | `df.filter(isinf(col("value")))` |
| `rand()` | Random number | `seed` | `df.select(rand(42))` |
| `randn()` | Random normal | `seed` | `df.select(randn(42))` |
| `bin()` | Binary representation | `col` | `df.select(bin(col("value")))` |
| `hex()` | Hexadecimal representation | `col` | `df.select(hex(col("value")))` |
| `unhex()` | Unhexadecimal | `col` | `df.select(unhex(col("hex_value")))` |
| `conv()` | Base conversion | `col, from_base, to_base` | `df.select(conv(col("value"), 10, 16))` |
| `bround()` | Banker's rounding | `col, scale` | `df.select(bround(col("value"), 2))` |

## Date/Time Functions

| Function | Purpose | Parameters | Example |
|----------|---------|------------|---------|
| `current_date()` | Current date | - | `df.select(current_date())` |
| `current_timestamp()` | Current timestamp | - | `df.select(current_timestamp())` |
| `date_format()` | Format date | `date, format` | `df.select(date_format(col("date"), "yyyy-MM-dd"))` |
| `to_date()` | Convert to date | `col, format` | `df.select(to_date(col("date_str"), "yyyy-MM-dd"))` |
| `to_timestamp()` | Convert to timestamp | `col, format` | `df.select(to_timestamp(col("ts_str"), "yyyy-MM-dd HH:mm:ss"))` |
| `year()` | Extract year | `col` | `df.select(year(col("date")))` |
| `month()` | Extract month | `col` | `df.select(month(col("date")))` |
| `dayofmonth()` | Extract day of month | `col` | `df.select(dayofmonth(col("date")))` |
| `dayofweek()` | Extract day of week | `col` | `df.select(dayofweek(col("date")))` |
| `dayofyear()` | Extract day of year | `col` | `df.select(dayofyear(col("date")))` |
| `hour()` | Extract hour | `col` | `df.select(hour(col("timestamp")))` |
| `minute()` | Extract minute | `col` | `df.select(minute(col("timestamp")))` |
| `second()` | Extract second | `col` | `df.select(second(col("timestamp")))` |
| `weekofyear()` | Extract week of year | `col` | `df.select(weekofyear(col("date")))` |
| `quarter()` | Extract quarter | `col` | `df.select(quarter(col("date")))` |
| `date_add()` | Add days to date | `start, days` | `df.select(date_add(col("date"), 30))` |
| `date_sub()` | Subtract days from date | `start, days` | `df.select(date_sub(col("date"), 30))` |
| `datediff()` | Days between dates | `end, start` | `df.select(datediff(col("end_date"), col("start_date")))` |
| `months_between()` | Months between dates | `end, start, roundOff` | `df.select(months_between(col("end"), col("start")))` |
| `add_months()` | Add months to date | `start, months` | `df.select(add_months(col("date"), 3))` |
| `next_day()` | Next occurrence of weekday | `date, dayOfWeek` | `df.select(next_day(col("date"), "Monday"))` |
| `last_day()` | Last day of month | `date` | `df.select(last_day(col("date")))` |
| `trunc()` | Truncate date | `date, format` | `df.select(trunc(col("date"), "month"))` |
| `date_trunc()` | Truncate timestamp | `format, timestamp` | `df.select(date_trunc("hour", col("timestamp")))` |
| `from_unixtime()` | Unix timestamp to string | `ut, format` | `df.select(from_unixtime(col("unix_time")))` |
| `unix_timestamp()` | String to unix timestamp | `timeExp, format` | `df.select(unix_timestamp(col("time_str")))` |
| `from_utc_timestamp()` | UTC to timezone | `ts, tz` | `df.select(from_utc_timestamp(col("utc_ts"), "PST"))` |
| `to_utc_timestamp()` | Timezone to UTC | `ts, tz` | `df.select(to_utc_timestamp(col("local_ts"), "PST"))` |
| `window()` | Time window | `timeColumn, windowDuration, slideDuration` | `df.groupBy(window(col("timestamp"), "10 minutes")).count()` |

## Array Functions

| Function | Purpose | Parameters | Example |
|----------|---------|------------|---------|
| `array()` | Create array | `*cols` | `df.select(array(col("a"), col("b")))` |
| `array_contains()` | Check if array contains value | `col, value` | `df.filter(array_contains(col("arr"), "value"))` |
| `array_distinct()` | Remove duplicates | `col` | `df.select(array_distinct(col("arr")))` |
| `array_except()` | Array difference | `col1, col2` | `df.select(array_except(col("arr1"), col("arr2")))` |
| `array_intersect()` | Array intersection | `col1, col2` | `df.select(array_intersect(col("arr1"), col("arr2")))` |
| `array_join()` | Join array elements | `col, delimiter, nullReplacement` | `df.select(array_join(col("arr"), ","))` |
| `array_max()` | Maximum value in array | `col` | `df.select(array_max(col("arr")))` |
| `array_min()` | Minimum value in array | `col` | `df.select(array_min(col("arr")))` |
| `array_position()` | Find position of element | `col, value` | `df.select(array_position(col("arr"), "value"))` |
| `array_remove()` | Remove all occurrences | `col, element` | `df.select(array_remove(col("arr"), "value"))` |
| `array_repeat()` | Repeat element n times | `col, count` | `df.select(array_repeat(col("value"), 3))` |
| `array_sort()` | Sort array | `col` | `df.select(array_sort(col("arr")))` |
| `array_union()` | Array union | `col1, col2` | `df.select(array_union(col("arr1"), col("arr2")))` |
| `arrays_overlap()` | Check if arrays overlap | `col1, col2` | `df.filter(arrays_overlap(col("arr1"), col("arr2")))` |
| `arrays_zip()` | Zip arrays together | `*cols` | `df.select(arrays_zip(col("arr1"), col("arr2")))` |
| `element_at()` | Get element at index | `col, extraction` | `df.select(element_at(col("arr"), 1))` |
| `explode()` | Explode array to rows | `col` | `df.select(explode(col("arr")))` |
| `posexplode()` | Explode with position | `col` | `df.select(posexplode(col("arr")))` |
| `reverse()` | Reverse array | `col` | `df.select(reverse(col("arr")))` |
| `shuffle()` | Shuffle array | `col` | `df.select(shuffle(col("arr")))` |
| `size()` | Get array size | `col` | `df.select(size(col("arr")))` |
| `slice()` | Get array slice | `x, start, length` | `df.select(slice(col("arr"), 1, 3))` |
| `sort_array()` | Sort array | `col, asc` | `df.select(sort_array(col("arr"), False))` |
| `flatten()` | Flatten nested arrays | `col` | `df.select(flatten(col("nested_arr")))` |
| `sequence()` | Generate sequence | `start, stop, step` | `df.select(sequence(lit(1), lit(10)))` |

## Map Functions

| Function | Purpose | Parameters | Example |
|----------|---------|------------|---------|
| `create_map()` | Create map | `*cols` | `df.select(create_map(col("k1"), col("v1")))` |
| `map_keys()` | Get map keys | `col` | `df.select(map_keys(col("map_col")))` |
| `map_values()` | Get map values | `col` | `df.select(map_values(col("map_col")))` |
| `map_entries()` | Get map entries | `col` | `df.select(map_entries(col("map_col")))` |
| `map_from_entries()` | Create map from entries | `col` | `df.select(map_from_entries(col("entries")))` |
| `map_from_arrays()` | Create map from arrays | `keys, values` | `df.select(map_from_arrays(col("keys"), col("values")))` |
| `map_concat()` | Concatenate maps | `*cols` | `df.select(map_concat(col("map1"), col("map2")))` |
| `element_at()` | Get value by key | `col, key` | `df.select(element_at(col("map_col"), "key"))` |
| `size()` | Get map size | `col` | `df.select(size(col("map_col")))` |
| `explode()` | Explode map to rows | `col` | `df.select(explode(col("map_col")))` |
| `posexplode()` | Explode map with position | `col` | `df.select(posexplode(col("map_col")))` |

## JSON Functions

| Function | Purpose | Parameters | Example |
|----------|---------|------------|---------|
| `from_json()` | Parse JSON string | `col, schema, options` | `df.select(from_json(col("json_str"), schema))` |
| `to_json()` | Convert to JSON string | `col, options` | `df.select(to_json(col("struct_col")))` |
| `json_tuple()` | Extract JSON fields | `jsonColumn, *fields` | `df.select(json_tuple(col("json"), "field1", "field2"))` |
| `get_json_object()` | Extract JSON object | `col, path` | `df.select(get_json_object(col("json"), "$.field"))` |
| `schema_of_json()` | Get JSON schema | `json` | `schema = spark.range(1).select(schema_of_json(lit('{"a":1}')))` |

## Struct Functions

| Function | Purpose | Parameters | Example |
|----------|---------|------------|---------|
| `struct()` | Create struct | `*cols` | `df.select(struct(col("a"), col("b")))` |
| `col()` | Access struct field | `col.field` | `df.select(col("struct_col.field"))` |
| `explode()` | Explode struct array | `col` | `df.select(explode(col("struct_array")))` |

## Null/Conditional Functions

| Function | Purpose | Parameters | Example |
|----------|---------|------------|---------|
| `isnull()` | Check if null | `col` | `df.filter(isnull(col("value")))` |
| `isnotnull()` | Check if not null | `col` | `df.filter(isnotnull(col("value")))` |
| `isnan()` | Check if NaN | `col` | `df.filter(isnan(col("value")))` |
| `coalesce()` | First non-null value | `*cols` | `df.select(coalesce(col("a"), col("b"), lit("default")))` |
| `when()` | Conditional expression | `condition, value` | `df.select(when(col("a") > 0, "positive").otherwise("negative"))` |
| `otherwise()` | Else clause for when | `value` | `when(col("a") > 0, "pos").otherwise("neg")` |
| `nanvl()` | Replace NaN with value | `col1, col2` | `df.select(nanvl(col("value"), lit(0)))` |
| `nullif()` | Return null if equal | `col1, col2` | `df.select(nullif(col("a"), col("b")))` |
| `nvl()` | Replace null with value | `col1, col2` | `df.select(nvl(col("value"), lit("default")))` |
| `nvl2()` | Replace null/not null | `col1, col2, col3` | `df.select(nvl2(col("a"), col("b"), col("c")))` |

## Type Conversion Functions

| Function | Purpose | Parameters | Example |
|----------|---------|------------|---------|
| `cast()` | Cast to data type | `dataType` | `df.select(col("str_col").cast("int"))` |
| `astype()` | Cast to data type (alias) | `dataType` | `df.select(col("str_col").astype("int"))` |
| `col()` | Reference column | `colName` | `df.select(col("column_name"))` |
| `lit()` | Create literal | `value` | `df.select(lit("literal_value"))` |
| `array()` | Create array literal | `*cols` | `df.select(array(lit(1), lit(2), lit(3)))` |
| `create_map()` | Create map literal | `*cols` | `df.select(create_map(lit("key"), lit("value")))` |
| `struct()` | Create struct literal | `*cols` | `df.select(struct(lit("a").alias("field1")))` |

## Aggregate Functions

| Function | Purpose | Parameters | Example |
|----------|---------|------------|---------|
| `sum()` | Sum of values | `col` | `df.groupBy("group").agg(sum("value"))` |
| `avg()` | Average of values | `col` | `df.groupBy("group").agg(avg("value"))` |
| `mean()` | Mean of values (alias) | `col` | `df.groupBy("group").agg(mean("value"))` |
| `count()` | Count of values | - | `df.groupBy("group").agg(count("*"))` |
| `countDistinct()` | Count distinct values | `col, *cols` | `df.groupBy("group").agg(countDistinct("value"))` |
| `max()` | Maximum value | `col` | `df.groupBy("group").agg(max("value"))` |
| `min()` | Minimum value | `col` | `df.groupBy("group").agg(min("value"))` |
| `first()` | First value | `col, ignorenulls` | `df.groupBy("group").agg(first("value"))` |
| `last()` | Last value | `col, ignorenulls` | `df.groupBy("group").agg(last("value"))` |
| `stddev()` | Standard deviation | `col` | `df.groupBy("group").agg(stddev("value"))` |
| `stddev_pop()` | Population std dev | `col` | `df.groupBy("group").agg(stddev_pop("value"))` |
| `stddev_samp()` | Sample std dev | `col` | `df.groupBy("group").agg(stddev_samp("value"))` |
| `variance()` | Variance | `col` | `df.groupBy("group").agg(variance("value"))` |
| `var_pop()` | Population variance | `col` | `df.groupBy("group").agg(var_pop("value"))` |
| `var_samp()` | Sample variance | `col` | `df.groupBy("group").agg(var_samp("value"))` |
| `collect_list()` | Collect values to list | `col` | `df.groupBy("group").agg(collect_list("value"))` |
| `collect_set()` | Collect values to set | `col` | `df.groupBy("group").agg(collect_set("value"))` |
| `skewness()` | Skewness | `col` | `df.groupBy("group").agg(skewness("value"))` |
| `kurtosis()` | Kurtosis | `col` | `df.groupBy("group").agg(kurtosis("value"))` |
| `approx_count_distinct()` | Approximate count distinct | `col, rsd` | `df.groupBy("group").agg(approx_count_distinct("value"))` |
| `corr()` | Correlation | `col1, col2` | `df.agg(corr("col1", "col2"))` |
| `covar_pop()` | Population covariance | `col1, col2` | `df.agg(covar_pop("col1", "col2"))` |
| `covar_samp()` | Sample covariance | `col1, col2` | `df.agg(covar_samp("col1", "col2"))` |

## Window Functions

| Function | Purpose | Parameters | Example |
|----------|---------|------------|---------|
| `row_number()` | Row number | - | `df.withColumn("rn", row_number().over(window))` |
| `rank()` | Rank with gaps | - | `df.withColumn("rank", rank().over(window))` |
| `dense_rank()` | Dense rank | - | `df.withColumn("dense_rank", dense_rank().over(window))` |
| `percent_rank()` | Percent rank | - | `df.withColumn("pct_rank", percent_rank().over(window))` |
| `ntile()` | N-tile | `n` | `df.withColumn("quartile", ntile(4).over(window))` |
| `lag()` | Previous row value | `col, offset, default` | `df.withColumn("prev", lag("value", 1).over(window))` |
| `lead()` | Next row value | `col, offset, default` | `df.withColumn("next", lead("value", 1).over(window))` |
| `first_value()` | First value in window | `col, ignorenulls` | `df.withColumn("first", first_value("value").over(window))` |
| `last_value()` | Last value in window | `col, ignorenulls` | `df.withColumn("last", last_value("value").over(window))` |
| `cume_dist()` | Cumulative distribution | - | `df.withColumn("cum_dist", cume_dist().over(window))` |

## Common Usage Patterns

### Import Required Functions
```python
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
```

### Window Specification
```python
window = Window.partitionBy("group").orderBy("timestamp")
windowSpec = Window.partitionBy("dept").orderBy("salary").rowsBetween(-1, 1)
```

### Chaining Functions
```python
df.select(
    upper(trim(col("name"))).alias("clean_name"),
    when(col("age") >= 18, "adult").otherwise("minor").alias("category")
)
```
