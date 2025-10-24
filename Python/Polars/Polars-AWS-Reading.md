# Polars AWS Reading
When working with Polars and AWS you can work with S3 as well as using the AWS CLI. To read all JSON files from an S3 folder using Polars, you can use the `scan_ndjson()` or `read_ndjson()` functions with a wildcard pattern. Here's how:

```python
import polars as pl

# For newline-delimited JSON files (most common)
# Using scan (lazy - more memory efficient)
df = pl.scan_ndjson("s3://your-bucket/your-folder/*.json").collect()

# Or using read (eager - loads immediately)
df = pl.read_ndjson("s3://your-bucket/your-folder/*.json")

# For standard JSON files (array of objects)
df = pl.read_json("s3://your-bucket/your-folder/*.json")
```

**Key points:**

1. **Credentials**: Polars uses the AWS SDK, so it will automatically use your AWS credentials from environment variables, `~/.aws/credentials`, or IAM roles.

2. **NDJSON vs JSON**: 
   - Use `read_ndjson()` if each file contains one JSON object per line
   - Use `read_json()` if each file is a single JSON array or object

3. **Lazy evaluation**: `scan_ndjson()` is more memory efficient for large datasets as it only loads data when you call `.collect()`

**Example with AWS credentials:**

```python
import os
import polars as pl

# Set credentials if not already configured
os.environ['AWS_ACCESS_KEY_ID'] = 'your-key'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'your-secret'
os.environ['AWS_REGION'] = 'us-east-1'

# Read all JSON files
df = pl.read_ndjson("s3://my-bucket/data/*.json")
```

The wildcard `*.json` will match all JSON files in that folder and concatenate them into a single DataFrame automatically.
