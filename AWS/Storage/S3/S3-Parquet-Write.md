# S3 Parquet Write
You can write Parquet files directly to S3 from memory without touching disk. Here are the main approaches:

---

## Option 1: PyArrow + boto3 (via BytesIO)

```python
import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO

# Your data
table = pa.table({"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"]})

# Write Parquet to an in-memory buffer
buffer = BytesIO()
pq.write_table(table, buffer)
buffer.seek(0)

# Upload directly to S3
s3 = boto3.client("s3")
s3.put_object(Bucket="my-bucket", Key="path/to/file.parquet", Body=buffer.getvalue())
```

---

## Option 2: Pandas + PyArrow + s3fs (simplest)

```python
import pandas as pd

df = pd.DataFrame({"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"]})

# s3fs handles the stream transparently
df.to_parquet("s3://my-bucket/path/to/file.parquet", engine="pyarrow")
```

> Requires: `pip install pandas pyarrow s3fs`

---

## Option 3: PyArrow native S3 filesystem

```python
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.fs as pafs

table = pa.table({"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"]})

s3 = pafs.S3FileSystem(region="us-east-1")

with s3.open_output_stream("my-bucket/path/to/file.parquet") as f:
    pq.write_table(table, f)
```

---

## Option 4: Polars (very fast, built-in S3 support)

```python
import polars as pl

df = pl.DataFrame({"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"]})

# Polars streams directly to S3 via object_store under the hood
df.write_parquet("s3://my-bucket/path/to/file.parquet")
```

> Requires: `pip install polars[cloud]`

---

## Comparison

| Approach | Deps | Best For |
|---|---|---|
| `BytesIO` + boto3 | pyarrow, boto3 | Fine-grained S3 control |
| pandas + s3fs | pandas, s3fs | Familiar pandas workflow |
| PyArrow native FS | pyarrow | Arrow-native pipelines |
| Polars | polars | Speed + simplicity |

**Recommended**: If you're already using pandas/pyarrow, go with **Option 2** — it's the cleanest. If you need low-level control (custom metadata, ACLs, encryption), use **Option 1** with `BytesIO`.
