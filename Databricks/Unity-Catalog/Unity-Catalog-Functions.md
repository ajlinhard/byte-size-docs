# Unity Catalog Functions
You can create functions in Databricks in several ways, and yes, most of these methods work for Spark as well since Databricks is built on Apache Spark. Here are the main approaches:

## 1. SQL User-Defined Functions (UDFs)

**In Databricks/Spark SQL:**
```sql
-- Create a simple SQL function
CREATE OR REPLACE FUNCTION calculate_tax(price DOUBLE, tax_rate DOUBLE)
RETURNS DOUBLE
LANGUAGE SQL
DETERMINISTIC
RETURN price * tax_rate;

-- Use the function
SELECT calculate_tax(100.0, 0.08) as tax_amount;
```

## 2. Python UDFs

**Register a Python function as a UDF:**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import DoubleType

spark = SparkSession.builder.getOrCreate()

# Define Python function
def calculate_tax(price, tax_rate):
    return price * tax_rate

# Register as UDF
calculate_tax_udf = udf(calculate_tax, DoubleType())

# Or register it globally
spark.udf.register("calculate_tax", calculate_tax, DoubleType())

# Use in DataFrame operations
df.withColumn("tax", calculate_tax_udf(df.price, df.tax_rate))

# Or use in SQL
spark.sql("SELECT calculate_tax(price, tax_rate) FROM my_table")
```

## 3. Pandas UDFs (Vectorized UDFs)

**For better performance with large datasets:**
```python
import pandas as pd
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import DoubleType

@pandas_udf(returnType=DoubleType())
def calculate_tax_pandas(price: pd.Series, tax_rate: pd.Series) -> pd.Series:
    return price * tax_rate

# Use it
df.withColumn("tax", calculate_tax_pandas(df.price, df.tax_rate))
```

## 4. Catalog Functions (Persistent Functions)

**Create functions that persist in the metastore:**
```python
# Using SQL
spark.sql("""
CREATE OR REPLACE FUNCTION my_catalog.my_schema.calculate_tax(price DOUBLE, tax_rate DOUBLE)
RETURNS DOUBLE
LANGUAGE PYTHON
AS $$
  return price * tax_rate
$$
""")

# List functions in catalog
spark.catalog.listFunctions().show()
```

## Key Differences Between Databricks and Open Source Spark:

**Databricks advantages:**
- Unity Catalog support for centralized function management
- Better integration with notebooks
- Enhanced security and governance features
- Support for more languages in SQL functions

**Compatibility:**
- Basic SQL UDFs work the same way
- Python UDFs are identical
- Pandas UDFs work the same
- Catalog-level functions may have different syntax/features

## Best Practices:

1. **Use Pandas UDFs** for better performance when processing large datasets
2. **SQL functions** are often faster than Python UDFs for simple operations
3. **Register functions globally** if you'll use them across multiple notebooks/sessions
4. **Use Unity Catalog** (in Databricks) for enterprise-wide function sharing

The core UDF functionality is the same between Databricks and open source Spark, but Databricks offers additional enterprise features and better integration with their platform.
