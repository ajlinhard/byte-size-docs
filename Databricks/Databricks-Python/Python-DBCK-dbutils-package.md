# Databricks dbutils Package
Databricks provides `dbutils` as a built-in utility package specifically for their platform. It's not a standard Python package that you'd install via pip - it's automatically available in Databricks notebooks and runtime environments.

The `dbutils` package provides several key utilities:

- **dbutils.fs** - File system operations (list, copy, move, delete files in DBFS, cloud storage, etc.)
- **dbutils.notebook** - Notebook workflow operations (run other notebooks, exit with values, etc.)
- **dbutils.widgets** - Create interactive widgets for parameterizing notebooks
- **dbutils.secrets** - Access secrets stored in Databricks secret scopes
- **dbutils.library** - Install and manage libraries (though this is less commonly used now)

You can explore available commands by running `dbutils.help()` in a Databricks notebook, or get help for specific modules like `dbutils.fs.help()`.

Outside of Databricks environments, `dbutils` won't be available, so code using it is specific to the Databricks platform.

## Advanced Usage Tips

**File System Operations:**
- Use `dbutils.fs.ls()` with error handling to check if paths exist
- The `recurse=True` parameter in `cp()` and `rm()` is crucial for directory operations
- Mount points persist across cluster restarts, but you should check if already mounted before mounting again

**Notebook Workflows:**
- The `timeout_seconds` parameter is important - set it generously for long-running jobs
- Return values from `dbutils.notebook.run()` are always strings, so parse them if you need other types
- Use `getContext()` to get information about the current execution environment

**Widgets Best Practices:**
- Create widgets at the top of your notebook for better organization
- Use `getArgument()` instead of `get()` when you want to provide defaults for parameters passed from other notebooks
- Remove widgets when they're no longer needed to keep the interface clean

**Security with Secrets:**
- Never log or print secret values - they won't show in the output anyway, but it's good practice
- Organize secrets into logical scopes (e.g., "database-prod", "api-keys", "certificates")
- Use `getBytes()` for binary data like certificates or keys

---
# Databricks dbutils Python Package Cheatsheet

## dbutils.fs (File System Operations)

| Function | Purpose | Parameters | Example |
|----------|---------|------------|---------|
| `ls()` | List files/directories | `dir` (string) | `dbutils.fs.ls("/mnt/data")` |
| `cp()` | Copy files/directories | `from` (string), `to` (string), `recurse` (bool) | `dbutils.fs.cp("/source/file.txt", "/dest/file.txt")` |
| `mv()` | Move/rename files | `from` (string), `to` (string) | `dbutils.fs.mv("/old/path", "/new/path")` |
| `rm()` | Remove files/directories | `dir` (string), `recurse` (bool) | `dbutils.fs.rm("/path/to/delete", True)` |
| `mkdirs()` | Create directories | `dir` (string) | `dbutils.fs.mkdirs("/new/directory")` |
| `head()` | Read first bytes of file | `file` (string), `max_bytes` (int) | `dbutils.fs.head("/data/file.txt", 1000)` |
| `put()` | Write string to file | `file` (string), `contents` (string), `overwrite` (bool) | `dbutils.fs.put("/path/file.txt", "content", True)` |
| `mount()` | Mount external storage | `source` (string), `mount_point` (string), `extra_configs` (dict) | `dbutils.fs.mount("s3a://bucket", "/mnt/s3")` |
| `unmount()` | Unmount storage | `mount_point` (string) | `dbutils.fs.unmount("/mnt/s3")` |
| `mounts()` | List all mounts | None | `dbutils.fs.mounts()` |
| `refreshMounts()` | Refresh mount cache | None | `dbutils.fs.refreshMounts()` |

### dbutils.fs Code Examples

```python
# List files with detailed info
files = dbutils.fs.ls("/databricks-datasets/")
for file in files:
    print(f"Name: {file.name}, Size: {file.size}, Path: {file.path}")

# Copy entire directory recursively
dbutils.fs.cp("/source/directory", "/destination/directory", recurse=True)

# Create nested directories
dbutils.fs.mkdirs("/deep/nested/directory/structure")

# Write and read files
dbutils.fs.put("/tmp/sample.txt", "Hello Databricks!", True)
content = dbutils.fs.head("/tmp/sample.txt")
print(content)

# Mount S3 bucket with authentication
dbutils.fs.mount(
    source="s3a://my-bucket/data",
    mount_point="/mnt/my-data",
    extra_configs={
        "fs.s3a.access.key": "your-access-key",
        "fs.s3a.secret.key": "your-secret-key"
    }
)

# Check if path exists (using try/except)
try:
    dbutils.fs.ls("/path/to/check")
    print("Path exists")
except:
    print("Path does not exist")
```

## dbutils.notebook (Notebook Workflow Operations)

| Function | Purpose | Parameters | Example |
|----------|---------|------------|---------|
| `run()` | Run another notebook | `path` (string), `timeout_seconds` (int), `arguments` (dict) | `dbutils.notebook.run("/other/notebook", 3600, {"param": "value"})` |
| `exit()` | Exit with return value | `value` (string) | `dbutils.notebook.exit("success")` |
| `getContext()` | Get notebook context | None | `dbutils.notebook.getContext()` |

### dbutils.notebook Code Examples

```python
# Run a data processing notebook with parameters
result = dbutils.notebook.run(
    "/data-processing/etl-pipeline", 
    timeout_seconds=7200,  # 2 hours
    arguments={
        "input_path": "/mnt/raw-data/2024/",
        "output_path": "/mnt/processed-data/",
        "date": "2024-01-15"
    }
)
print(f"ETL result: {result}")

# Conditional notebook execution
if success_condition:
    dbutils.notebook.run("/success-workflow", 1800)
else:
    dbutils.notebook.run("/failure-workflow", 1800)

# Exit with status
if error_occurred:
    dbutils.notebook.exit("FAILED: Data validation errors found")
else:
    dbutils.notebook.exit("SUCCESS: Pipeline completed")

# Get current notebook context
context = dbutils.notebook.getContext()
print(f"Notebook path: {context.notebookPath}")
print(f"Cluster ID: {context.clusterId}")
```

## dbutils.widgets (Interactive Widgets)

| Function | Purpose | Parameters | Example |
|----------|---------|------------|---------|
| `text()` | Create text input | `name` (string), `defaultValue` (string), `label` (string) | `dbutils.widgets.text("filename", "data.csv", "File Name")` |
| `dropdown()` | Create dropdown | `name` (string), `defaultValue` (string), `choices` (list), `label` (string) | `dbutils.widgets.dropdown("env", "dev", ["dev", "prod"])` |
| `combobox()` | Create combobox | `name` (string), `defaultValue` (string), `choices` (list), `label` (string) | `dbutils.widgets.combobox("table", "users", ["users", "orders"])` |
| `multiselect()` | Create multiselect | `name` (string), `defaultValue` (string), `choices` (list), `label` (string) | `dbutils.widgets.multiselect("columns", "id", ["id", "name"])` |
| `get()` | Get widget value | `name` (string) | `dbutils.widgets.get("filename")` |
| `getArgument()` | Get parameter value | `name` (string), `defaultValue` (string) | `dbutils.widgets.getArgument("date", "2024-01-01")` |
| `remove()` | Remove specific widget | `name` (string) | `dbutils.widgets.remove("filename")` |
| `removeAll()` | Remove all widgets | None | `dbutils.widgets.removeAll()` |

### dbutils.widgets Code Examples

```python
# Create parameter widgets for a data pipeline
dbutils.widgets.text("input_path", "/mnt/raw-data/", "Input Data Path")
dbutils.widgets.dropdown("environment", "dev", ["dev", "staging", "prod"], "Environment")
dbutils.widgets.combobox("table_name", "users", ["users", "orders", "products"], "Table Name")
dbutils.widgets.multiselect("columns", "id,name", ["id", "name", "email", "created_at"], "Columns to Process")

# Get widget values
input_path = dbutils.widgets.get("input_path")
environment = dbutils.widgets.get("environment")
table_name = dbutils.widgets.get("table_name")
selected_columns = dbutils.widgets.get("columns").split(",")

print(f"Processing {table_name} from {input_path} in {environment} environment")
print(f"Selected columns: {selected_columns}")

# Use getArgument for notebook parameters (from dbutils.notebook.run)
date_param = dbutils.widgets.getArgument("processing_date", "2024-01-01")
batch_size = int(dbutils.widgets.getArgument("batch_size", "1000"))

# Clean up widgets when done
dbutils.widgets.removeAll()
```

## dbutils.secrets (Secret Management)

| Function | Purpose | Parameters | Example |
|----------|---------|------------|---------|
| `get()` | Get secret value | `scope` (string), `key` (string) | `dbutils.secrets.get("my-scope", "api-key")` |
| `getBytes()` | Get secret as bytes | `scope` (string), `key` (string) | `dbutils.secrets.getBytes("my-scope", "binary-key")` |
| `list()` | List secrets in scope | `scope` (string) | `dbutils.secrets.list("my-scope")` |
| `listScopes()` | List all scopes | None | `dbutils.secrets.listScopes()` |

### dbutils.secrets Code Examples

```python
# Access database credentials
db_password = dbutils.secrets.get("database-secrets", "postgres-password")
api_key = dbutils.secrets.get("api-keys", "openai-key")

# Use secrets in connection strings
connection_string = f"postgresql://user:{db_password}@host:5432/database"

# List available secrets (for debugging)
scopes = dbutils.secrets.listScopes()
for scope in scopes:
    print(f"Scope: {scope.name}")
    secrets = dbutils.secrets.list(scope.name)
    for secret in secrets:
        print(f"  Secret: {secret.key}")

# Access binary secrets
cert_bytes = dbutils.secrets.getBytes("certificates", "ssl-cert")
```

## dbutils.library (Library Management)

| Function | Purpose | Parameters | Example |
|----------|---------|------------|---------|
| `installPyPI()` | Install PyPI package | `package` (string), `version` (string), `repo` (string) | `dbutils.library.installPyPI("pandas", "1.5.0")` |
| `install()` | Install library from path | `path` (string) | `dbutils.library.install("/path/to/library.jar")` |
| `list()` | List installed libraries | None | `dbutils.library.list()` |
| `restartPython()` | Restart Python process | None | `dbutils.library.restartPython()` |

### dbutils.library Code Examples

```python
# Install specific package versions
dbutils.library.installPyPI("scikit-learn", "1.3.0")
dbutils.library.installPyPI("matplotlib", "3.7.1")

# Install from custom repository
dbutils.library.installPyPI(
    "my-custom-package", 
    "1.0.0", 
    repo="https://my-private-pypi.com/simple"
)

# Install JAR file
dbutils.library.install("/dbfs/jars/custom-spark-connector.jar")

# Restart Python to use new libraries
dbutils.library.restartPython()

# Check installed libraries
libraries = dbutils.library.list()
for lib in libraries:
    print(f"Library: {lib.library}, Status: {lib.status}")
```

## Common Usage Patterns

### File Processing Pipeline
```python
# Setup parameters
dbutils.widgets.text("input_date", "2024-01-01", "Processing Date")
dbutils.widgets.dropdown("format", "parquet", ["parquet", "csv", "json"], "Output Format")

date = dbutils.widgets.get("input_date")
output_format = dbutils.widgets.get("format")

# Process files
input_path = f"/mnt/raw-data/{date}/"
output_path = f"/mnt/processed-data/{date}/"

# Check input exists
try:
    files = dbutils.fs.ls(input_path)
    print(f"Found {len(files)} files to process")
except:
    dbutils.notebook.exit(f"ERROR: Input path {input_path} not found")

# Create output directory
dbutils.fs.mkdirs(output_path)

# Process data (your processing logic here)
# df = spark.read.parquet(input_path)
# df.write.format(output_format).save(output_path)

dbutils.notebook.exit(f"SUCCESS: Processed {len(files)} files to {output_path}")
```

### Secure Data Access
```python
# Get credentials from secrets
aws_access_key = dbutils.secrets.get("aws-secrets", "access-key")
aws_secret_key = dbutils.secrets.get("aws-secrets", "secret-key")
db_password = dbutils.secrets.get("database", "prod-password")

# Mount S3 with credentials
dbutils.fs.mount(
    source="s3a://my-data-lake/",
    mount_point="/mnt/data-lake",
    extra_configs={
        "fs.s3a.access.key": aws_access_key,
        "fs.s3a.secret.key": aws_secret_key
    }
)

# Connect to database
connection_url = f"jdbc:postgresql://db.company.com:5432/prod?user=analytics&password={db_password}"
```

### Multi-Notebook Workflow
```python
# Master notebook orchestrating multiple steps
steps = [
    {"notebook": "/etl/step1-extract", "timeout": 1800},
    {"notebook": "/etl/step2-transform", "timeout": 3600},
    {"notebook": "/etl/step3-load", "timeout": 1200}
]

for i, step in enumerate(steps):
    print(f"Running step {i+1}: {step['notebook']}")
    try:
        result = dbutils.notebook.run(
            step["notebook"], 
            step["timeout"],
            {"batch_date": "2024-01-01", "step_number": str(i+1)}
        )
        print(f"Step {i+1} completed: {result}")
    except Exception as e:
        print(f"Step {i+1} failed: {str(e)}")
        dbutils.notebook.exit(f"FAILED at step {i+1}")

dbutils.notebook.exit("SUCCESS: All steps completed")
```

## Tips and Best Practices

1. **Error Handling**: Always wrap file operations in try/except blocks
2. **Path Conventions**: Use `/dbfs/` for local file system, `/mnt/` for mounted storage
3. **Widget Cleanup**: Call `dbutils.widgets.removeAll()` to clean up widgets
4. **Secret Security**: Never print or log secret values
5. **Timeouts**: Set appropriate timeouts for notebook.run() based on expected execution time
6. **Mount Management**: Unmount storage when no longer needed to free resources
