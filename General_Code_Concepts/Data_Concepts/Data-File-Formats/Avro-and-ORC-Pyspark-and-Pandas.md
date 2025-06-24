# Using Avro and ORC in Pyspark and Pandas
Yes, both pandas and PySpark can read Avro and ORC files, though with different levels of native support and some caveats. Here's a comprehensive overview:## **Quick Summary:**

### **Pandas Support:**

**Avro Files:**
- ✅ **Supported** via third-party libraries (`fastavro`, `pandavro`)
- 🏆 **Best option**: `fastavro` for performance
- ❌ **No native support** in pandas

**ORC Files:**
- ✅ **Native support** since pandas 1.5.0 with `pd.read_orc()`
- ✅ **PyArrow backend** provides excellent performance
- 🏆 **Best option**: `pd.read_orc()` or PyArrow directly

### **PySpark Support:**

**Avro Files:**
- ✅ **Excellent support** with spark-avro package
- 🏆 **Best for**: Large distributed datasets
- 📦 **Requires**: `spark-avro` package configuration

**ORC Files:**
- ✅ **Native built-in support** (no extra packages needed)
- 🏆 **Exceptional performance** for analytics workloads
- ⭐ **Highly optimized** for big data scenarios

## **Key Installation Commands:**

```bash
# For pandas
pip install pandas pyarrow fastavro

# For PySpark  
pip install pyspark

# Spark configuration for Avro
# Add to SparkSession: .config("spark.jars.packages", "org.apache.spark:spark-avro_2.12:3.4.0")
```

## **When to Use What:**

- **Small files + Quick analysis**: Pandas with appropriate libraries
- **Large files + Distributed processing**: PySpark
- **Analytics workloads**: PySpark + ORC (best performance)
- **Schema evolution needs**: Avro format with either tool
- **Data warehousing**: PySpark + ORC
- **Data exchange/streaming**: Avro format

Both tools handle these formats well, but PySpark excels with larger datasets while pandas is perfect for smaller-scale analysis and exploration.

---
# Code:
```python
# ============================================================================
# READING AVRO AND ORC FILES IN PANDAS AND PYSPARK
# ============================================================================

import pandas as pd
from pyspark.sql import SparkSession
import os

# Initialize Spark Session (needed for PySpark examples)
def create_spark_session():
    """Create Spark session with necessary configurations"""
    spark = SparkSession.builder \
        .appName("AvroOrcExample") \
        .config("spark.jars.packages", 
                "org.apache.spark:spark-avro_2.12:3.4.0,org.apache.orc:orc-core:1.8.0") \
        .getOrCreate()
    return spark

# ============================================================================
# PANDAS - AVRO FILES
# ============================================================================

def read_avro_with_pandas_fastavro(file_path):
    """
    Read Avro files in pandas using fastavro
    Installation: pip install fastavro
    """
    try:
        import fastavro
        import io
        
        records = []
        with open(file_path, 'rb') as f:
            reader = fastavro.reader(f)
            for record in reader:
                records.append(record)
        
        df = pd.DataFrame(records)
        print(f"✅ Pandas + fastavro: Read {len(df)} rows from {file_path}")
        return df
    
    except ImportError:
        print("❌ fastavro not installed. Run: pip install fastavro")
        return None

def read_avro_with_pandas_pandavro(file_path):
    """
    Read Avro files in pandas using pandavro
    Installation: pip install pandavro
    """
    try:
        import pandavro as pdx
        
        df = pdx.read_avro(file_path)
        print(f"✅ Pandas + pandavro: Read {len(df)} rows from {file_path}")
        return df
    
    except ImportError:
        print("❌ pandavro not installed. Run: pip install pandavro")
        return None

# ============================================================================
# PANDAS - ORC FILES  
# ============================================================================

def read_orc_with_pandas_pyarrow(file_path):
    """
    Read ORC files in pandas using PyArrow
    Installation: pip install pyarrow
    """
    try:
        import pyarrow.orc as orc
        
        # Read ORC file
        table = orc.read_table(file_path)
        df = table.to_pandas()
        
        print(f"✅ Pandas + PyArrow: Read {len(df)} rows from {file_path}")
        return df
    
    except ImportError:
        print("❌ PyArrow not installed. Run: pip install pyarrow")
        return None
    except Exception as e:
        print(f"❌ Error reading ORC file: {e}")
        return None

def read_orc_with_pandas_native(file_path):
    """
    Read ORC files using pandas native support (pandas >= 1.5.0)
    """
    try:
        # Pandas native ORC reading (requires pyarrow backend)
        df = pd.read_orc(file_path)
        print(f"✅ Pandas native: Read {len(df)} rows from {file_path}")
        return df
    
    except Exception as e:
        print(f"❌ Error with pandas native ORC reading: {e}")
        print("💡 Make sure you have pandas >= 1.5.0 and pyarrow installed")
        return None

# ============================================================================
# PYSPARK - AVRO FILES
# ============================================================================

def read_avro_with_pyspark(spark, file_path):
    """
    Read Avro files with PySpark
    Requires spark-avro package
    """
    try:
        # Read Avro file
        df = spark.read.format("avro").load(file_path)
        
        print(f"✅ PySpark Avro: Read {df.count()} rows from {file_path}")
        print("Schema:")
        df.printSchema()
        
        return df
    
    except Exception as e:
        print(f"❌ Error reading Avro with PySpark: {e}")
        print("💡 Make sure spark-avro package is available")
        return None

def write_avro_with_pyspark(spark, df, output_path):
    """
    Write DataFrame as Avro file with PySpark
    """
    try:
        df.write.format("avro").mode("overwrite").save(output_path)
        print(f"✅ PySpark: Written Avro file to {output_path}")
    
    except Exception as e:
        print(f"❌ Error writing Avro with PySpark: {e}")

# ============================================================================
# PYSPARK - ORC FILES
# ============================================================================

def read_orc_with_pyspark(spark, file_path):
    """
    Read ORC files with PySpark (native support)
    """
    try:
        # PySpark has native ORC support
        df = spark.read.format("orc").load(file_path)
        
        print(f"✅ PySpark ORC: Read {df.count()} rows from {file_path}")
        print("Schema:")
        df.printSchema()
        
        return df
    
    except Exception as e:
        print(f"❌ Error reading ORC with PySpark: {e}")
        return None

def write_orc_with_pyspark(spark, df, output_path):
    """
    Write DataFrame as ORC file with PySpark
    """
    try:
        df.write.format("orc").mode("overwrite").save(output_path)
        print(f"✅ PySpark: Written ORC file to {output_path}")
    
    except Exception as e:
        print(f"❌ Error writing ORC with PySpark: {e}")

# ============================================================================
# COMPARISON AND EXAMPLES
# ============================================================================

def create_sample_data():
    """Create sample data for testing"""
    data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'salary': [50000, 60000, 70000, 55000, 65000],
        'department': ['Engineering', 'Marketing', 'Sales', 'HR', 'Engineering']
    }
    return pd.DataFrame(data)

def comprehensive_example():
    """
    Comprehensive example showing all methods
    """
    print("🚀 COMPREHENSIVE AVRO & ORC READING EXAMPLE")
    print("=" * 60)
    
    # Create sample data
    sample_df = create_sample_data()
    print("📊 Sample data created:")
    print(sample_df)
    print()
    
    # Initialize Spark
    spark = create_spark_session()
    spark_df = spark.createDataFrame(sample_df)
    
    # Test file paths
    avro_file = "test_data.avro"
    orc_file = "test_data.orc"
    
    print("📝 WRITING TEST FILES")
    print("-" * 30)
    
    # Write test files using PySpark
    write_avro_with_pyspark(spark, spark_df, avro_file)
    write_orc_with_pyspark(spark, spark_df, orc_file)
    print()
    
    print("📖 READING AVRO FILES")
    print("-" * 30)
    
    # Read Avro with different methods
    df_avro_fastavro = read_avro_with_pandas_fastavro(avro_file + "/part-00000-*.avro")
    df_avro_pandavro = read_avro_with_pandas_pandavro(avro_file + "/part-00000-*.avro")
    df_avro_pyspark = read_avro_with_pyspark(spark, avro_file)
    print()
    
    print("📖 READING ORC FILES")
    print("-" * 30)
    
    # Read ORC with different methods
    df_orc_pyarrow = read_orc_with_pandas_pyarrow(orc_file + "/part-00000-*.orc")
    df_orc_pandas = read_orc_with_pandas_native(orc_file + "/part-00000-*.orc")
    df_orc_pyspark = read_orc_with_pyspark(spark, orc_file)
    print()
    
    # Clean up
    spark.stop()
    
    print("✨ Example completed!")

# ============================================================================
# PERFORMANCE COMPARISON
# ============================================================================

def performance_comparison_tips():
    """
    Performance tips for different scenarios
    """
    tips = """
    🚀 PERFORMANCE COMPARISON & TIPS
    ================================
    
    📊 PANDAS PERFORMANCE:
    ----------------------
    Avro:
    • fastavro: ⭐⭐⭐⭐⭐ (Fastest for pandas)
    • pandavro: ⭐⭐⭐ (Good, but slower than fastavro)
    • avro-python3: ⭐⭐ (Slowest, not recommended for large files)
    
    ORC:
    • PyArrow: ⭐⭐⭐⭐⭐ (Excellent performance, columnar optimizations)
    • pandas native: ⭐⭐⭐⭐⭐ (Same as PyArrow under the hood)
    
    🔥 PYSPARK PERFORMANCE:
    ----------------------
    Avro:
    • Native PySpark: ⭐⭐⭐⭐ (Good for distributed processing)
    • Best for: Large files, distributed computing
    
    ORC:
    • Native PySpark: ⭐⭐⭐⭐⭐ (Excellent, highly optimized)
    • Best for: Analytics workloads, data warehousing
    
    📈 RECOMMENDATIONS:
    ------------------
    Small-Medium files (<1GB):
    • Avro: Use pandas + fastavro
    • ORC: Use pandas + PyArrow
    
    Large files (>1GB):
    • Use PySpark for both formats
    • Leverage distributed processing
    
    Analytics workloads:
    • Prefer ORC format
    • Use PySpark for best performance
    
    Data exchange:
    • Prefer Avro format
    • Schema evolution capabilities
    """
    print(tips)

# ============================================================================
# INSTALLATION GUIDE
# ============================================================================

def installation_guide():
    """
    Complete installation guide
    """
    guide = """
    📦 INSTALLATION GUIDE
    ====================
    
    For Pandas + Avro:
    ------------------
    pip install pandas fastavro
    # OR
    pip install pandas pandavro
    
    For Pandas + ORC:
    ----------------
    pip install pandas pyarrow
    # Make sure pandas >= 1.5.0 for native ORC support
    
    For PySpark + Avro:
    ------------------
    pip install pyspark
    # Then configure Spark with spark-avro package:
    spark = SparkSession.builder \\
        .config("spark.jars.packages", "org.apache.spark:spark-avro_2.12:3.4.0") \\
        .getOrCreate()
    
    For PySpark + ORC:
    -----------------
    pip install pyspark
    # ORC support is built-in, no additional packages needed
    
    Complete setup for all formats:
    ------------------------------
    pip install pandas pyspark pyarrow fastavro pandavro
    """
    print(guide)

# Example usage
if __name__ == "__main__":
    installation_guide()
    print()
    performance_comparison_tips()
    print()
    
    # Uncomment to run comprehensive example:
    # comprehensive_example()
```
