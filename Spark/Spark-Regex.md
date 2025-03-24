# PySpark Regex Cheatsheet

Here's a comprehensive cheatsheet for using regex in PySpark, highlighting key differences from Python's regex:

## Basic PySpark Regex Functions

```python
from pyspark.sql.functions import regexp_extract, regexp_replace, col, when, rlike
```

| Function | Purpose | Example |
|----------|---------|---------|
| `regexp_extract(col, pattern, idx)` | Extract matching groups | `regexp_extract(col("text"), "(\d+)", 1)` |
| `regexp_replace(col, pattern, replacement)` | Replace matches | `regexp_replace(col("text"), "old", "new")` |
| `rlike(pattern)` | Filter rows matching pattern | `df.filter(col("text").rlike("pattern"))` |
| `like(pattern)` | SQL LIKE pattern matching | `df.filter(col("text").like("%word%"))` |

## Key Differences from Python Regex

1. **Engine Difference**: PySpark uses Java's regex engine (java.util.regex), not Python's re module

2. **Lookaround Syntax**:
   - Python: `(?<=foo)bar` (lookbehind)
   - Spark: Same syntax, but more limitations on variable-length patterns

3. **Backreferences**:
   - Python: `\1`, `\2` etc.
   - Spark: `$1`, `$2` etc. in replacement strings

4. **Non-Capturing Groups**:
   - Both use `(?:pattern)` but behavior can differ in complex expressions

5. **Unicode Support**:
   - Python: `\p{L}` with `re.UNICODE` flag
   - Spark: Directly supports `\p{L}` (Unicode letter property)

6. **Performance Considerations**:
   - Spark optimizes for distributed processing
   - Complex regex can be more costly in Spark due to serialization/distribution

## Common Patterns

```python
# Email validation
df.filter(col("email").rlike("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"))

# US Phone number extraction
regexp_extract(col("text"), "(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})", 1)

# Extract date (YYYY-MM-DD)
regexp_extract(col("text"), "(\d{4}-\d{2}-\d{2})", 1)

# IP address validation
df.filter(col("ip").rlike("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"))
```

## Escape Character Notes

PySpark regex often requires double-escaping backslashes in string literals:
```python
# Python: "\d+"
# PySpark: "\\d+"
```

## Performance Tips

1. Prefer simpler patterns when possible
2. For complex operations, consider:
   ```python
   # Register as temp view and use Spark SQL
   df.createOrReplaceTempView("my_table")
   spark.sql("SELECT regexp_extract(col, '(pattern)', 1) FROM my_table")
   ```

3. For very complex regex, consider pre-processing with UDFs (but be aware of performance trade-offs)

## Using regexp_replace with Backreferences

```python
# Reformat dates from MM-DD-YYYY to YYYY-MM-DD
regexp_replace(col("date"), "^(\\d{2})-(\\d{2})-(\\d{4})$", "$3-$1-$2")
```

Remember that since PySpark runs on the JVM, it follows Java's regex conventions rather than Python's, which can lead to subtle differences in behavior for complex patterns.
---
## PySpark Regex Operations
First, you'll need to import the necessary functions:

```python
from pyspark.sql.functions import regexp_extract, regexp_replace, col, when, expr
```

Here are the most common regex operations in PySpark:

### 1. Extract patterns with regexp_extract

```python
# Extract the first digit sequence from a text column
df = df.withColumn("extracted_digits", 
                   regexp_extract(col("text_column"), r"(\d+)", 1))
```

The function takes three arguments:
- Column to extract from
- Regex pattern (with capturing groups in parentheses)
- Group index to extract (0 for the entire match, 1 for the first group, etc.)

### 2. Replace patterns with regexp_replace

```python
# Replace phone numbers with masked version
df = df.withColumn("masked_text", 
                   regexp_replace(col("text_column"), r"\d{3}-\d{3}-\d{4}", "XXX-XXX-XXXX"))
```

### 3. Filter rows based on regex matches

```python
# Keep only rows where the email column has a valid email format
df = df.filter(col("email").rlike(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"))
```

### 4. Creating boolean flags for matches

```python
# Create flag indicating if text contains a URL
df = df.withColumn("contains_url", 
                   when(col("text_column").rlike(r"https?://\S+"), True).otherwise(False))
```

### 5. Multiple regex operations with expr

```python
# Use SQL expressions for more complex regex operations
df = df.withColumn("transformed", 
                   expr("regexp_replace(regexp_replace(text_column, '[0-9]', '#'), '[@]', '!')")
```

Remember that PySpark uses Java's regex engine, which has some differences from Python's regex syntax. For example, lookbehind and lookahead assertions have different syntax than in standard Python.

Would you like me to explain any of these regex operations in more detail or provide examples for a specific use case?
