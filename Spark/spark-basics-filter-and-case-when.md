
# Spark Filters and Case-When
Below is a comprehensive PySpark cheat sheet covering filters and case when statements. The guide includes:

**Filtering Techniques:**
- String filters (equals, contains, like, regex)
- Numeric comparisons and ranges
- Null/NaN handling
- Complex conditions with AND/OR logic
- Array, map, and date filtering

**Case When Patterns:**
- Basic conditional logic
- Nested conditions
- Mathematical operations
- Data cleaning applications
- Multi-level categorization

**Advanced Topics:**
- Combining filters with case when statements
- Performance optimization tips
- Common real-world patterns
- Dynamic filtering approaches
- SQL vs DataFrame API comparisons

The examples are practical and ready to use in your PySpark applications. Each section builds from simple concepts to more complex scenarios you might encounter in data processing workflows.
---
## Code Examples:
# PySpark Filters and Case When Cheat Sheet

## Basic Setup

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, otherwise, lit, isnull, isnan
from pyspark.sql.types import *

spark = SparkSession.builder.appName("FiltersCaseWhen").getOrCreate()
```

## Basic Filtering

### String Filters

```python
# Equal to
df.filter(col("name") == "John")
df.filter(df.name == "John")

# Not equal to
df.filter(col("name") != "John")
df.filter(~(col("name") == "John"))

# Contains
df.filter(col("name").contains("John"))

# Starts with / Ends with
df.filter(col("name").startswith("J"))
df.filter(col("name").endswith("n"))

# Like (SQL-style wildcards)
df.filter(col("name").like("J%"))
df.filter(col("name").like("%oh%"))

# Regex matching
df.filter(col("name").rlike("^J.*n$"))

# Case insensitive filtering
df.filter(col("name").lower() == "john")
```

### Numeric Filters

```python
# Basic comparisons
df.filter(col("age") > 25)
df.filter(col("age") >= 25)
df.filter(col("age") < 65)
df.filter(col("age") <= 65)

# Between
df.filter(col("age").between(25, 65))

# In a list
df.filter(col("age").isin([25, 30, 35]))

# Not in a list
df.filter(~col("age").isin([25, 30, 35]))
```

### Null and NaN Filters

```python
# Is null
df.filter(col("name").isNull())
df.filter(isnull(col("name")))

# Is not null
df.filter(col("name").isNotNull())
df.filter(~isnull(col("name")))

# Is NaN (for numeric columns)
df.filter(isnan(col("score")))

# Is not NaN
df.filter(~isnan(col("score")))
```

## Advanced Filtering

### Multiple Conditions

```python
# AND conditions
df.filter((col("age") > 25) & (col("salary") > 50000))

# OR conditions
df.filter((col("age") > 65) | (col("salary") > 100000))

# Complex combinations
df.filter(
    ((col("age") > 25) & (col("age") < 65)) |
    (col("department") == "Executive")
)

# Using multiple filter calls (equivalent to AND)
df.filter(col("age") > 25) \
  .filter(col("salary") > 50000)
```

### Array and Map Filters

```python
# Array contains
df.filter(col("skills").contains("Python"))

# Array size
df.filter(col("skills").size() > 2)

# Map key exists
df.filter(col("metadata").contains("key1"))
```

### Date Filters

```python
from pyspark.sql.functions import to_date, year, month, dayofweek

# Date comparisons
df.filter(col("hire_date") > "2020-01-01")
df.filter(col("hire_date").between("2020-01-01", "2022-12-31"))

# Year/Month/Day filters
df.filter(year(col("hire_date")) == 2021)
df.filter(month(col("hire_date")) == 12)
df.filter(dayofweek(col("hire_date")) == 2)  # Monday
```

## Case When Statements

### Basic Case When

```python
# Simple case when
df.withColumn("age_group", 
    when(col("age") < 18, "Minor")
    .when(col("age") < 65, "Adult")
    .otherwise("Senior")
)

# With multiple conditions
df.withColumn("bonus_eligible",
    when((col("performance") == "Excellent") & (col("tenure") > 2), True)
    .when(col("performance") == "Outstanding", True)
    .otherwise(False)
)
```

### Nested Case When

```python
# Nested conditions
df.withColumn("salary_grade",
    when(col("department") == "Engineering",
        when(col("level") == "Senior", "E-Senior")
        .when(col("level") == "Junior", "E-Junior")
        .otherwise("E-Mid")
    )
    .when(col("department") == "Sales",
        when(col("experience") > 5, "S-Experienced")
        .otherwise("S-New")
    )
    .otherwise("Other")
)
```

### Case When with Calculations

```python
# Mathematical operations in case when
df.withColumn("adjusted_salary",
    when(col("performance") == "Excellent", col("salary") * 1.2)
    .when(col("performance") == "Good", col("salary") * 1.1)
    .when(col("performance") == "Poor", col("salary") * 0.9)
    .otherwise(col("salary"))
)

# String operations
df.withColumn("display_name",
    when(col("first_name").isNull(), col("last_name"))
    .when(col("last_name").isNull(), col("first_name"))
    .otherwise(col("first_name") + " " + col("last_name"))
)
```

### Case When for Data Cleaning

```python
# Replace values
df.withColumn("gender_clean",
    when(col("gender").isin(["M", "Male", "MALE"]), "Male")
    .when(col("gender").isin(["F", "Female", "FEMALE"]), "Female")
    .otherwise("Unknown")
)

# Handle nulls and empty strings
df.withColumn("department_clean",
    when((col("department").isNull()) | (col("department") == ""), "Unknown")
    .otherwise(col("department"))
)
```

## Combining Filters and Case When

```python
# Filter then case when
result = df.filter(col("active") == True) \
    .withColumn("status",
        when(col("last_login") > "2023-01-01", "Active")
        .when(col("last_login") > "2022-01-01", "Inactive")
        .otherwise("Dormant")
    )

# Case when then filter
result = df.withColumn("risk_level",
    when(col("credit_score") < 600, "High")
    .when(col("credit_score") < 750, "Medium")
    .otherwise("Low")
) \
.filter(col("risk_level") != "High")
```

## Performance Tips

```python
# Use column references for better performance
# Good
df.filter(col("age") > 25)

# Less optimal for complex expressions
df.filter("age > 25")

# Push filters early in the pipeline
df.filter(col("active") == True) \
  .groupBy("department") \
  .agg({"salary": "avg"})

# Use broadcast for small lookup tables
broadcast_df = spark.sql("SELECT * FROM small_lookup_table")
result = df.join(broadcast(broadcast_df), "key")
```

## Common Patterns

### Multi-level Categorization

```python
def categorize_employee(df):
    return df.withColumn("category",
        when((col("level") == "Senior") & (col("performance") == "Excellent"), "Top Performer")
        .when((col("level") == "Senior") & (col("performance") == "Good"), "Senior Good")
        .when((col("level") == "Mid") & (col("performance") == "Excellent"), "Rising Star")
        .when(col("performance") == "Poor", "Needs Improvement")
        .otherwise("Standard")
    )
```

### Data Quality Flags

```python
def add_quality_flags(df):
    return df.withColumn("data_quality",
        when(col("email").isNull() | ~col("email").contains("@"), "Invalid Email")
        .when(col("phone").isNull() | (col("phone").length() < 10), "Invalid Phone")
        .when(col("age") < 0, "Invalid Age")
        .otherwise("Valid")
    )
```

### Dynamic Filtering

```python
def dynamic_filter(df, conditions):
    """Apply multiple filter conditions dynamically"""
    result = df
    for condition in conditions:
        result = result.filter(condition)
    return result

# Usage
conditions = [
    col("age") > 25,
    col("department").isin(["Engineering", "Sales"]),
    col("active") == True
]
filtered_df = dynamic_filter(df, conditions)
```

## SQL vs DataFrame API

```python
# SQL style
spark.sql("""
    SELECT *,
        CASE 
            WHEN age < 18 THEN 'Minor'
            WHEN age < 65 THEN 'Adult'
            ELSE 'Senior'
        END as age_group
    FROM employees
    WHERE department = 'Engineering' AND salary > 50000
""")

# DataFrame API equivalent
df.filter((col("department") == "Engineering") & (col("salary") > 50000)) \
  .withColumn("age_group",
    when(col("age") < 18, "Minor")
    .when(col("age") < 65, "Adult")
    .otherwise("Senior")
  )
```
