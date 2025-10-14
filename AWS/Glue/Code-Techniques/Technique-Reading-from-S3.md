# Glue Reading from S3
Below will show you how to load `.ocr` files containing JSON data into a Spark DataFrame using AWS Glue.I've provided **4 different approaches** to load `.ocr` files containing JSON data in AWS Glue. Here's when to use each:

## **Approach 1: Direct Path Pattern (Simplest)**
Best when all your files are in one directory without recursion needed. The `*.ocr` pattern directly filters files.

## **Approach 2: Glue DynamicFrame with Filter**
Good for leveraging Glue's optimization while still filtering by extension. Uses `input_file_name()` to filter.

## **Approach 3: Hadoop FileSystem API**
Provides more control for complex filtering logic and works well with recursive directory structures.

## **Approach 4: boto3 Listing (Most Flexible)**
Best for complex filtering requirements or when you need additional file metadata. Most flexible but adds boto3 dependency.

**Approach 4 DOES utilize Spark's parallelism for reading/processing**, but the **file listing with boto3 happens sequentially on the driver node**. Here's what actually happens:

1. **boto3 listing** - Sequential on driver (not parallelized)
2. **spark.read.json(file_list)** - Parallelized across executors ✓

The actual **data reading and processing is still distributed**, but if you have millions of files, the listing itself could be a bottleneck.## **Best Recommendations:**

**For most use cases, use Approach 1:**
```python
df = spark.read.json("s3://bucket/path/*.ocr")
```
This is **fully parallelized** - Spark's execution engine handles both discovery and reading in a distributed manner.

**Approach 2 is also fully parallelized** if you use Glue's catalog or read with patterns, but filtering by filename after reading is less efficient.

**Approaches 3 & 4** have the same limitation - sequential file listing on the driver, then parallel reading. Use these only when:
- You need complex filtering logic beyond file extensions
- You need file metadata (size, timestamps) for filtering
- You're dealing with a reasonable number of files (<100k)

## **Performance Comparison:**
- **Approach 1**: ⚡⚡⚡ Fully distributed, fastest
- **Approach 2**: ⚡⚡ Reads everything then filters
- **Approach 3**: ⚡⚡ Sequential listing + parallel read
- **Approach 4**: ⚡⚡ Sequential listing + parallel read

### **Key Options for Semi-Structured JSON:**

- **`multiline: true`** - For JSON objects spanning multiple lines
- **`mode: PERMISSIVE`** - Handles corrupt/malformed records gracefully
- **`columnNameOfCorruptRecord`** - Captures problematic records for debugging
- 
**Bottom line:** Stick with **Approach 1** unless you have specific filtering requirements that patterns can't handle!

```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
import boto3

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# ===================================================================
# APPROACH 1: List files and batch them manually (Most Control)
# ===================================================================

def get_files_from_s3(bucket, prefix, extension=".ocr"):
    """List all files matching criteria from S3"""
    s3_client = boto3.client('s3')
    files = []
    
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
    
    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                key = obj['Key']
                if key.endswith(extension):
                    files.append(f"s3://{bucket}/{key}")
    
    return files

def chunk_list(lst, chunk_size):
    """Split list into chunks"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

# Get all files
bucket = "your-bucket"
prefix = "your-path/"
all_files = get_files_from_s3(bucket, prefix, ".ocr")

print(f"Total files found: {len(all_files)}")

# Process in batches
batch_size = 100  # Process 100 files at a time
batch_num = 0

for file_batch in chunk_list(all_files, batch_size):
    batch_num += 1
    print(f"Processing batch {batch_num} with {len(file_batch)} files")
    
    # Read this batch
    df = spark.read.json(file_batch)
    
    # Process the batch
    # ... your transformations here ...
    
    # Write batch output
    output_path = f"s3://output-bucket/output/batch_{batch_num}/"
    df.write.mode("overwrite").parquet(output_path)
    
    print(f"Batch {batch_num} completed")

# ===================================================================
# APPROACH 2: Using Glue Job Bookmarks (Automatic State Management)
# ===================================================================

# Enable job bookmarks in your Glue job configuration
# This automatically tracks which files have been processed

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
job.init(args['JOB_NAME'], args)

# Read with job bookmarks enabled
datasource = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={
        "paths": ["s3://your-bucket/your-path/"],
        "recurse": True,
        "exclusions": ["**/*.tmp", "**/_*"]  # Exclude temp files
    },
    format="json",
    transformation_ctx="datasource"  # Required for bookmarks
)

# Process the data
df = datasource.toDF()
# ... your transformations ...

# Write output
output_frame = DynamicFrame.fromDF(df, glueContext, "output_frame")
glueContext.write_dynamic_frame.from_options(
    frame=output_frame,
    connection_type="s3",
    connection_options={"path": "s3://output-bucket/output/"},
    format="parquet",
    transformation_ctx="output"  # Required for bookmarks
)

job.commit()  # Commit bookmark state

# ===================================================================
# APPROACH 3: Batch by File Count using RDD Partitioning
# ===================================================================

def process_files_in_batches_rdd(file_list, batch_size):
    """Process files using RDD partitioning for parallelism"""
    
    # Create batches
    batches = list(chunk_list(file_list, batch_size))
    
    # Parallelize batches as RDD
    batch_rdd = sc.parallelize(batches, len(batches))
    
    def process_batch(file_batch):
        """Process a single batch of files"""
        # Read files in this batch
        df = spark.read.json(list(file_batch))
        
        # Add batch identifier
        from pyspark.sql.functions import lit, monotonically_increasing_id
        batch_id = hash(tuple(file_batch)) % 10000
        df = df.withColumn("batch_id", lit(batch_id))
        
        return df
    
    # Process each batch
    for i, batch in enumerate(batches):
        df = process_batch(batch)
        # Process and write
        output_path = f"s3://output-bucket/output/batch_{i}/"
        df.write.mode("overwrite").parquet(output_path)

# Usage
all_files = get_files_from_s3(bucket, prefix)
process_files_in_batches_rdd(all_files, batch_size=50)

# ===================================================================
# APPROACH 4: Batch by Date Partitions (for partitioned data)
# ===================================================================

from datetime import datetime, timedelta

def process_by_date_range(start_date, end_date, date_format="%Y-%m-%d"):
    """Process files organized by date partitions"""
    
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime(date_format)
        date_path = f"s3://bucket/data/year={current_date.year}/month={current_date.month:02d}/day={current_date.day:02d}/"
        
        print(f"Processing date: {date_str}")
        
        try:
            df = spark.read.json(f"{date_path}*.ocr")
            
            # Process this date's data
            # ... transformations ...
            
            # Write output
            output_path = f"s3://output-bucket/output/date={date_str}/"
            df.write.mode("overwrite").parquet(output_path)
            
        except Exception as e:
            print(f"No data or error for {date_str}: {e}")
        
        current_date += timedelta(days=1)

# Usage
start = datetime(2024, 1, 1)
end = datetime(2024, 1, 31)
process_by_date_range(start, end)

# ===================================================================
# APPROACH 5: Streaming-style batch processing with foreachBatch
# ===================================================================

def process_batch_streaming(batch_df, batch_id):
    """Process each micro-batch"""
    print(f"Processing batch {batch_id}")
    
    # Your transformations
    from pyspark.sql.functions import current_timestamp
    batch_df = batch_df.withColumn("processed_at", current_timestamp())
    
    # Write output
    batch_df.write \
        .mode("append") \
        .parquet(f"s3://output-bucket/output/")

# For structured streaming (if new files arrive continuously)
# Note: This requires trigger intervals and is for streaming scenarios
streaming_df = spark.readStream \
    .format("json") \
    .option("maxFilesPerTrigger", 10)  # Batch size: 10 files per trigger
    .load("s3://bucket/path/*.ocr")

query = streaming_df.writeStream \
    .foreachBatch(process_batch_streaming) \
    .outputMode("append") \
    .start()

# query.awaitTermination()  # Keep running for streaming

# ===================================================================
# APPROACH 6: Memory-efficient batch processing with limits
# ===================================================================

def process_with_memory_limit(files, max_size_mb=500):
    """Batch files by total size to avoid memory issues"""
    s3_client = boto3.client('s3')
    
    current_batch = []
    current_size = 0
    batch_num = 0
    
    for file_path in files:
        # Parse S3 path
        bucket = file_path.replace("s3://", "").split("/")[0]
        key = "/".join(file_path.replace("s3://", "").split("/")[1:])
        
        # Get file size
        response = s3_client.head_object(Bucket=bucket, Key=key)
        file_size_mb = response['ContentLength'] / (1024 * 1024)
        
        if current_size + file_size_mb > max_size_mb and current_batch:
            # Process current batch
            batch_num += 1
            print(f"Processing batch {batch_num} ({current_size:.2f} MB)")
            df = spark.read.json(current_batch)
            # ... process and write ...
            
            # Reset for next batch
            current_batch = [file_path]
            current_size = file_size_mb
        else:
            current_batch.append(file_path)
            current_size += file_size_mb
    
    # Process final batch
    if current_batch:
        batch_num += 1
        print(f"Processing final batch {batch_num} ({current_size:.2f} MB)")
        df = spark.read.json(current_batch)
        # ... process and write ...

# Usage
all_files = get_files_from_s3(bucket, prefix)
process_with_memory_limit(all_files, max_size_mb=1000)  # 1GB batches
```
