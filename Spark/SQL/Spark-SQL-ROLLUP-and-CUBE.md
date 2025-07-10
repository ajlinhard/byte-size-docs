# Spark SQL ROLLUP and CUBE
I'll walk you through how ROLLUP and CUBE qualifiers work in Spark SQL's GROUP BY statements, then provide examples with sample data.

### Table of Contents
- [Understanding ROLLUP and CUBE](#Understanding-ROLLUP-and-CUBE)
- [Use Cases](#Use-Cases)
- [Jump to Code Examples](#Code-Examples)

## Understanding ROLLUP and CUBE
Both ROLLUP and CUBE are extensions to GROUP BY that generate multiple levels of aggregation in a single query, but they work differently:

### ROLLUP
- Creates a **hierarchical** set of groupings
- Assumes there's a natural hierarchy in your grouping columns
- Generates subtotals from left to right, removing one column at a time
- Always includes a grand total row

### CUBE
- Creates **all possible combinations** of grouping columns
- Generates subtotals for every possible subset of the grouping columns
- Includes partial totals for each individual column and their combinations
- Also includes a grand total row

## How They Generate Groups

For `GROUP BY ROLLUP(A, B, C)`:
1. `(A, B, C)` - Full grouping
2. `(A, B)` - Remove rightmost column
3. `(A)` - Remove next rightmost column
4. `()` - Grand total (no grouping)

For `GROUP BY CUBE(A, B, C)`:
1. `(A, B, C)` - All columns
2. `(A, B)`, `(A, C)`, `(B, C)` - All 2-column combinations
3. `(A)`, `(B)`, `(C)` - Each individual column
4. `()` - Grand total (no grouping)Let me also show you what the actual output would look like with some key examples:## Summary

**ROLLUP** and **CUBE** are powerful SQL extensions that save you from writing multiple GROUP BY queries with UNION ALL. Here's when to use each:

- **ROLLUP**: Perfect for hierarchical data where you want subtotals that "roll up" naturally (like geographic regions, time periods, or organizational structures)
- **CUBE**: Ideal for dimensional analysis where you want to see all possible combinations of your grouping columns

The key insight is that ROLLUP assumes a hierarchy in your columns (left to right), while CUBE treats all columns as independent dimensions and generates every possible combination.

Both are incredibly useful for creating comprehensive reports and dashboards with multiple levels of aggregation in a single, efficient query!

---
# Use Cases
Great question! While ROLLUP and CUBE are most commonly associated with BI reporting and ad-hoc analysis, they actually have several interesting applications in machine learning and data science workflows. Let me break down the use cases:

## Traditional Use Cases

### 1. **BI Reporting & Dashboards**
- Financial reports with subtotals (department → team → individual)
- Sales dashboards with regional breakdowns
- Performance metrics across multiple dimensions

### 2. **Ad-hoc Analysis**
- Exploratory data analysis to understand data distributions
- Quick cross-tabulation for business stakeholders
- Data validation and quality checks

## Machine Learning Use Cases

### 1. **Feature Engineering**
```python
# Creating aggregated features at multiple levels
# For a customer churn model:
spark.sql("""
    SELECT customer_id, 
           region, product_category,
           AVG(transaction_amount) as avg_transaction,
           SUM(transaction_amount) as total_spent,
           COUNT(*) as transaction_count
    FROM transactions
    GROUP BY ROLLUP(customer_id, region, product_category)
""")
# This creates features at customer level, region level, and category level
```

### 2. **Data Preprocessing & Aggregation**
- **Time Series Features**: Using ROLLUP with time dimensions (year, month, week) to create lagged features
- **Hierarchical Features**: Customer → Segment → Industry aggregations for recommendation systems
- **Multi-level Embeddings**: Aggregating user behavior at different granularities

### 3. **Model Validation & Analysis**
```python
# Analyzing model performance across multiple dimensions
spark.sql("""
    SELECT model_version, data_segment, feature_group,
           AVG(accuracy) as avg_accuracy,
           AVG(precision) as avg_precision,
           COUNT(*) as num_predictions
    FROM model_predictions
    GROUP BY CUBE(model_version, data_segment, feature_group)
""")
# Helps identify which combinations cause model performance issues
```

### 4. **Anomaly Detection**
- **Statistical Baselines**: Using ROLLUP to establish normal ranges at different aggregation levels
- **Outlier Detection**: Comparing individual records against rolled-up statistics
- **Threshold Setting**: Establishing alerts based on deviations from historical aggregations

### 5. **Recommendation Systems**
```python
# Content-based filtering with multi-level preferences
spark.sql("""
    SELECT user_id, genre, subgenre,
           AVG(rating) as avg_rating,
           COUNT(*) as interaction_count
    FROM user_interactions
    GROUP BY ROLLUP(user_id, genre, subgenre)
""")
# Creates preference profiles at user, genre, and subgenre levels
```

### 6. **A/B Testing & Experimentation**
- **Stratified Analysis**: Using CUBE to analyze experiment results across multiple dimensions
- **Segment Performance**: Understanding how different user segments respond to treatments
- **Interaction Effects**: Identifying combinations of factors that influence outcomes

## Advanced Data Science Applications

### 1. **Hierarchical Clustering Preparation**
```python
# Preparing data for hierarchical clustering
spark.sql("""
    SELECT region, city, neighborhood,
           AVG(house_price) as avg_price,
           STDDEV(house_price) as price_std
    FROM real_estate
    GROUP BY ROLLUP(region, city, neighborhood)
""")
# Creates features at different geographic levels for clustering
```

### 2. **Time Series Decomposition**
```python
# Multi-level time series aggregation
spark.sql("""
    SELECT year, quarter, month,
           SUM(sales) as total_sales,
           AVG(sales) as avg_sales
    FROM sales_data
    GROUP BY ROLLUP(year, quarter, month)
""")
# Useful for seasonal decomposition and trend analysis
```

### 3. **Causal Inference**
- **Simpson's Paradox Detection**: Using CUBE to identify confounding variables
- **Stratified Treatment Effects**: Analyzing intervention impacts across subgroups
- **Propensity Score Matching**: Creating matched groups at different levels

### 4. **Deep Learning Data Preparation**
```python
# Creating training data for hierarchical neural networks
spark.sql("""
    SELECT category_l1, category_l2, category_l3,
           AVG(embedding_dim_1) as avg_emb_1,
           AVG(embedding_dim_2) as avg_emb_2
    FROM product_embeddings
    GROUP BY ROLLUP(category_l1, category_l2, category_l3)
""")
# Useful for hierarchical softmax or structured embeddings
```

## Why These Work Well for ML

### **Computational Efficiency**
- Single query instead of multiple aggregations
- Leverages Spark's optimization for grouped operations
- Reduces data shuffling in distributed environments

### **Feature Consistency**
- Ensures consistent aggregation logic across different levels
- Maintains referential integrity between features
- Simplifies feature pipeline maintenance

### **Handles Missing Data Gracefully**
- Automatically creates higher-level aggregations when lower-level data is sparse
- Provides fallback values for cold-start problems
- Enables robust model training with incomplete data

## Performance Considerations

**Pros:**
- More efficient than multiple separate GROUP BY queries
- Leverages SQL engine optimizations
- Reduces data movement in distributed systems

**Cons:**
- Can create very large result sets (especially CUBE)
- May not be suitable for high-cardinality dimensions
- Memory intensive for complex hierarchies

## When NOT to Use for ML

- **High-cardinality dimensions**: User IDs, timestamps at second level
- **Real-time inference**: Too slow for online serving
- **Simple aggregations**: When you only need one level of aggregation
- **Streaming data**: Better suited for batch processing

The key insight is that ROLLUP and CUBE are particularly valuable in ML workflows where you need **consistent multi-level aggregations** and **hierarchical features**. They're especially powerful in feature engineering pipelines where you want to capture patterns at different granularities without writing complex, error-prone aggregation logic.


---
# Code Examples
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, count, avg

# Initialize Spark session
spark = SparkSession.builder \
    .appName("ROLLUP and CUBE Examples") \
    .getOrCreate()

# Sample sales data
sales_data = [
    ("North", "Electronics", "Laptop", 1500),
    ("North", "Electronics", "Phone", 800),
    ("North", "Clothing", "Shirt", 50),
    ("North", "Clothing", "Pants", 80),
    ("South", "Electronics", "Laptop", 1600),
    ("South", "Electronics", "Tablet", 400),
    ("South", "Clothing", "Shirt", 45),
    ("South", "Clothing", "Dress", 120),
    ("West", "Electronics", "Phone", 750),
    ("West", "Electronics", "Laptop", 1550),
    ("West", "Clothing", "Pants", 85),
    ("East", "Electronics", "Tablet", 420),
    ("East", "Clothing", "Shirt", 55),
    ("East", "Clothing", "Dress", 110)
]

# Create DataFrame
columns = ["region", "category", "product", "sales"]
df = spark.createDataFrame(sales_data, columns)

print("=== SAMPLE DATA ===")
df.show()

# Register as temporary view for SQL queries
df.createOrReplaceTempView("sales")

print("\n=== REGULAR GROUP BY (for comparison) ===")
spark.sql("""
    SELECT region, category, SUM(sales) as total_sales
    FROM sales
    GROUP BY region, category
    ORDER BY region, category
""").show()

print("\n=== GROUP BY ROLLUP Examples ===")

# ROLLUP with 2 columns
print("ROLLUP(region, category):")
spark.sql("""
    SELECT region, category, SUM(sales) as total_sales
    FROM sales
    GROUP BY ROLLUP(region, category)
    ORDER BY region, category
""").show()

# ROLLUP with 3 columns
print("ROLLUP(region, category, product):")
spark.sql("""
    SELECT region, category, product, SUM(sales) as total_sales, COUNT(*) as item_count
    FROM sales
    GROUP BY ROLLUP(region, category, product)
    ORDER BY region, category, product
""").show(50)

print("\n=== GROUP BY CUBE Examples ===")

# CUBE with 2 columns
print("CUBE(region, category):")
spark.sql("""
    SELECT region, category, SUM(sales) as total_sales
    FROM sales
    GROUP BY CUBE(region, category)
    ORDER BY region, category
""").show()

# CUBE with 3 columns (partial results - this gets large!)
print("CUBE(region, category, product) - First 20 rows:")
spark.sql("""
    SELECT region, category, product, SUM(sales) as total_sales, COUNT(*) as item_count
    FROM sales
    GROUP BY CUBE(region, category, product)
    ORDER BY region, category, product
""").show(20)

print("\n=== Using GROUPING Function to Identify Aggregation Levels ===")

# GROUPING function returns 1 if the column is aggregated (NULL in result), 0 otherwise
print("ROLLUP with GROUPING function:")
spark.sql("""
    SELECT 
        region,
        category,
        SUM(sales) as total_sales,
        GROUPING(region) as region_grouped,
        GROUPING(category) as category_grouped,
        CASE 
            WHEN GROUPING(region) = 1 AND GROUPING(category) = 1 THEN 'Grand Total'
            WHEN GROUPING(region) = 0 AND GROUPING(category) = 1 THEN 'Region Subtotal'
            ELSE 'Detail'
        END as aggregation_level
    FROM sales
    GROUP BY ROLLUP(region, category)
    ORDER BY region, category
""").show()

print("\n=== Practical Business Examples ===")

# Sales report with subtotals
print("Sales Report with Regional and Category Subtotals:")
spark.sql("""
    SELECT 
        COALESCE(region, 'ALL REGIONS') as region,
        COALESCE(category, 'ALL CATEGORIES') as category,
        SUM(sales) as total_sales,
        ROUND(AVG(sales), 2) as avg_sales,
        COUNT(*) as item_count
    FROM sales
    GROUP BY ROLLUP(region, category)
    ORDER BY region, category
""").show()

# Cross-tabulation style report
print("Cross-tabulation Analysis (CUBE):")
spark.sql("""
    SELECT 
        COALESCE(region, 'TOTAL') as region,
        COALESCE(category, 'TOTAL') as category,
        SUM(sales) as total_sales,
        COUNT(*) as transactions
    FROM sales
    GROUP BY CUBE(region, category)
    ORDER BY 
        CASE WHEN region = 'TOTAL' THEN 1 ELSE 0 END,
        region,
        CASE WHEN category = 'TOTAL' THEN 1 ELSE 0 END,
        category
""").show()

# Stop Spark session
spark.stop()

print("\n=== Key Differences Summary ===")
print("""
ROLLUP vs CUBE:

ROLLUP(A, B, C) generates 4 grouping levels:
- (A, B, C) - Full detail
- (A, B) - Subtotal removing C
- (A) - Subtotal removing B and C  
- () - Grand total

CUBE(A, B, C) generates 8 grouping levels:
- (A, B, C) - Full detail
- (A, B), (A, C), (B, C) - All 2-column combinations
- (A), (B), (C) - Each individual column
- () - Grand total

Use ROLLUP when you have hierarchical data (like Region > Category > Product)
Use CUBE when you want all possible cross-tabulations
""")
```

# Expected Output Examples for ROLLUP and CUBE

## Sample Data
```
+------+-----------+-------+-----+
|region|   category|product|sales|
+------+-----------+-------+-----+
| North|Electronics| Laptop| 1500|
| North|Electronics|  Phone|  800|
| North|   Clothing|  Shirt|   50|
| North|   Clothing|  Pants|   80|
| South|Electronics| Laptop| 1600|
| South|Electronics| Tablet|  400|
| South|   Clothing|  Shirt|   45|
| South|   Clothing|  Dress|  120|
|  West|Electronics|  Phone|  750|
|  West|Electronics| Laptop| 1550|
|  West|   Clothing|  Pants|   85|
|  East|Electronics| Tablet|  420|
|  East|   Clothing|  Shirt|   55|
|  East|   Clothing|  Dress|  110|
+------+-----------+-------+-----+
```

## GROUP BY ROLLUP(region, category) Output
```
+------+-----------+-----------+
|region|   category|total_sales|
+------+-----------+-----------+
|  East|   Clothing|        165|  -- Detail: East + Clothing
|  East|Electronics|        420|  -- Detail: East + Electronics
|  East|       null|        585|  -- Subtotal: East (all categories)
| North|   Clothing|        130|  -- Detail: North + Clothing
| North|Electronics|       2300|  -- Detail: North + Electronics
| North|       null|       2430|  -- Subtotal: North (all categories)
| South|   Clothing|        165|  -- Detail: South + Clothing
| South|Electronics|       2000|  -- Detail: South + Electronics
| South|       null|       2165|  -- Subtotal: South (all categories)
|  West|   Clothing|         85|  -- Detail: West + Clothing
|  West|Electronics|       2300|  -- Detail: West + Electronics
|  West|       null|       2385|  -- Subtotal: West (all categories)
|  null|       null|       7565|  -- Grand Total: All regions, all categories
+------+-----------+-----------+
```

## GROUP BY CUBE(region, category) Output
```
+------+-----------+-----------+
|region|   category|total_sales|
+------+-----------+-----------+
|  null|   Clothing|        545|  -- All regions, Clothing only
|  null|Electronics|       7020|  -- All regions, Electronics only
|  null|       null|       7565|  -- Grand Total: All regions, all categories
|  East|   Clothing|        165|  -- Detail: East + Clothing
|  East|Electronics|        420|  -- Detail: East + Electronics
|  East|       null|        585|  -- Subtotal: East (all categories)
| North|   Clothing|        130|  -- Detail: North + Clothing
| North|Electronics|       2300|  -- Detail: North + Electronics
| North|       null|       2430|  -- Subtotal: North (all categories)
| South|   Clothing|        165|  -- Detail: South + Clothing
| South|Electronics|       2000|  -- Detail: South + Electronics
| South|       null|       2165|  -- Subtotal: South (all categories)
|  West|   Clothing|         85|  -- Detail: West + Clothing
|  West|Electronics|       2300|  -- Detail: West + Electronics
|  West|       null|       2385|  -- Subtotal: West (all categories)
+------+-----------+-----------+
```

## Key Observations:

### ROLLUP produces hierarchical subtotals:
- **Detail rows**: Each region-category combination
- **Regional subtotals**: Each region with all categories combined (category = null)
- **Grand total**: All regions and categories (both = null)

### CUBE produces all possible combinations:
- **Detail rows**: Each region-category combination (same as ROLLUP)
- **Regional subtotals**: Each region with all categories (same as ROLLUP)
- **Category subtotals**: Each category across all regions (region = null)
- **Grand total**: All regions and categories (both = null)

### The key difference:
CUBE adds the **category-only subtotals** (where region = null but category has a value), showing totals for each category across all regions. ROLLUP doesn't include these.

## Using GROUPING Function Example:
```
+------+-----------+-----------+--------------+----------------+------------------+
|region|   category|total_sales|region_grouped|category_grouped|aggregation_level|
+------+-----------+-----------+--------------+----------------+------------------+
|  East|   Clothing|        165|             0|               0|            Detail|
|  East|Electronics|        420|             0|               0|            Detail|
|  East|       null|        585|             0|               1|  Region Subtotal|
| North|   Clothing|        130|             0|               0|            Detail|
| North|Electronics|       2300|             0|               0|            Detail|
| North|       null|       2430|             0|               1|  Region Subtotal|
| South|   Clothing|        165|             0|               0|            Detail|
| South|Electronics|       2000|             0|               0|            Detail|
| South|       null|       2165|             0|               1|  Region Subtotal|
|  West|   Clothing|         85|             0|               0|            Detail|
|  West|Electronics|       2300|             0|               0|            Detail|
|  West|       null|       2385|             0|               1|  Region Subtotal|
|  null|       null|       7565|             1|               1|      Grand Total|
+------+-----------+-----------+--------------+----------------+------------------+
```

## When to Use Each:

**Use ROLLUP when:**
- You have hierarchical data (Time → Year → Quarter → Month)
- You want subtotals that roll up naturally (Region → State → City)
- You need fewer aggregation levels for performance

**Use CUBE when:**
- You want all possible cross-tabulations
- You're doing exploratory data analysis
- You need to see totals for each dimension independently
- You're building OLAP-style reports
