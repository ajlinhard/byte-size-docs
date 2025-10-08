# POLARS JSON OPERATIONS CHEATSHEET

```python
import polars as pl
import json

# ============================================================================
# READING JSON FILES
# ============================================================================

# Read JSON file (line-delimited/NDJSON)
df = pl.read_json('data.json')

# Read NDJSON (newline-delimited JSON - one JSON object per line)
df = pl.read_ndjson('data.ndjson')

# Lazy reading for large files
lazy_df = pl.scan_ndjson('data.ndjson')
df = lazy_df.collect()

# Read from string
json_string = '{"name": "Alice", "age": 25}'
df = pl.read_json(json_string.encode())

# Read JSON array
json_array = '[{"name": "Alice"}, {"name": "Bob"}]'
df = pl.read_json(json_array.encode())

# ============================================================================
# WRITING JSON FILES
# ============================================================================

# Write as NDJSON (recommended for large datasets)
df.write_ndjson('output.ndjson')

# Write as JSON array
df.write_json('output.json')

# Write with pretty formatting
df.write_json('output.json', pretty=True)

# Convert to JSON string
json_str = df.write_json()

# ============================================================================
# WORKING WITH JSON COLUMNS (Nested JSON Data)
# ============================================================================

# Example: DataFrame with JSON string column
df = pl.DataFrame({
    'id': [1, 2, 3],
    'data': [
        '{"name": "Alice", "age": 25, "city": "NYC"}',
        '{"name": "Bob", "age": 30, "city": "LA"}',
        '{"name": "Charlie", "age": 35, "city": "Chicago"}'
    ]
})

# Parse JSON string column
df_parsed = df.with_columns(
    pl.col('data').str.json_decode().alias('parsed_data')
)

# Extract specific fields from JSON
df_extracted = df.with_columns([
    pl.col('data').str.json_extract('$.name').alias('name'),
    pl.col('data').str.json_extract('$.age').alias('age'),
    pl.col('data').str.json_extract('$.city').alias('city')
])

# ============================================================================
# EXTRACTING NESTED JSON FIELDS
# ============================================================================

# Example: DataFrame with struct column (parsed JSON)
df = pl.DataFrame({
    'id': [1, 2, 3],
    'user': [
        {'name': 'Alice', 'age': 25, 'address': {'city': 'NYC', 'zip': '10001'}},
        {'name': 'Bob', 'age': 30, 'address': {'city': 'LA', 'zip': '90001'}},
        {'name': 'Charlie', 'age': 35, 'address': {'city': 'Chicago', 'zip': '60601'}}
    ]
})

# Extract top-level fields from struct
df.with_columns([
    pl.col('user').struct.field('name').alias('name'),
    pl.col('user').struct.field('age').alias('age')
])

# Extract nested fields
df.with_columns([
    pl.col('user').struct.field('address').struct.field('city').alias('city'),
    pl.col('user').struct.field('address').struct.field('zip').alias('zip')
])

# Unnest all fields from struct
df.unnest('user')

# Unnest nested struct
df.unnest('user').unnest('address')

# ============================================================================
# WORKING WITH JSON ARRAYS
# ============================================================================

# Example: JSON array in column
df = pl.DataFrame({
    'id': [1, 2, 3],
    'tags': [
        ['python', 'data', 'analytics'],
        ['javascript', 'web'],
        ['rust', 'systems', 'performance', 'fast']
    ]
})

# Get array length
df.with_columns(
    pl.col('tags').list.len().alias('num_tags')
)

# Get first element
df.with_columns(
    pl.col('tags').list.first().alias('first_tag')
)

# Get last element
df.with_columns(
    pl.col('tags').list.last().alias('last_tag')
)

# Get element at index
df.with_columns(
    pl.col('tags').list.get(0).alias('tag_0')
)

# Explode array (one row per element)
df.explode('tags')

# Check if array contains value
df.with_columns(
    pl.col('tags').list.contains('python').alias('has_python')
)

# Join array elements into string
df.with_columns(
    pl.col('tags').list.join(', ').alias('tags_string')
)

# ============================================================================
# COMPLEX JSON PARSING EXAMPLES
# ============================================================================

# Example 1: Parsing JSON string with nested objects
json_data = """
[
    {"id": 1, "user": {"name": "Alice", "email": "alice@example.com"}, "scores": [85, 90, 92]},
    {"id": 2, "user": {"name": "Bob", "email": "bob@example.com"}, "scores": [78, 88, 91]},
    {"id": 3, "user": {"name": "Charlie", "email": "charlie@example.com"}, "scores": [95, 93, 89]}
]
"""

df = pl.read_json(json_data.encode())

# Unnest user information
df_flat = (df
    .unnest('user')
    .with_columns([
        pl.col('scores').list.mean().alias('avg_score'),
        pl.col('scores').list.max().alias('max_score')
    ])
)

# Example 2: Working with deeply nested JSON
df = pl.DataFrame({
    'data': [
        {
            'id': 1,
            'user': {
                'profile': {
                    'name': 'Alice',
                    'contact': {'email': 'alice@example.com', 'phone': '123-456'}
                }
            }
        }
    ]
})

# Extract deeply nested fields
df.with_columns(
    pl.col('data')
    .struct.field('user')
    .struct.field('profile')
    .struct.field('contact')
    .struct.field('email')
    .alias('email')
)

# ============================================================================
# HANDLING MISSING/NULL VALUES IN JSON
# ============================================================================

# JSON with optional fields
df = pl.DataFrame({
    'data': [
        {'name': 'Alice', 'age': 25, 'city': 'NYC'},
        {'name': 'Bob', 'age': 30},  # missing 'city'
        {'name': 'Charlie', 'city': 'Chicago'}  # missing 'age'
    ]
})

# Extract with null handling
df.with_columns([
    pl.col('data').struct.field('name').alias('name'),
    pl.col('data').struct.field('age').alias('age'),
    pl.col('data').struct.field('city').alias('city')
])

# Fill nulls with default values
df.with_columns([
    pl.col('data').struct.field('age').fill_null(0).alias('age'),
    pl.col('data').struct.field('city').fill_null('Unknown').alias('city')
])

# ============================================================================
# CREATING JSON FROM DATAFRAME
# ============================================================================

# Create struct column (JSON-like structure)
df = pl.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35]
})

# Combine columns into struct
df.with_columns(
    pl.struct(['name', 'age']).alias('user_data')
)

# Create nested structure
df.with_columns(
    pl.struct([
        pl.col('name'),
        pl.struct(['age', 'id']).alias('metadata')
    ]).alias('nested_data')
)

# ============================================================================
# JSON PATH EXTRACTION
# ============================================================================

# Using json_extract with JSONPath
df = pl.DataFrame({
    'json_str': [
        '{"user": {"name": "Alice", "scores": [85, 90, 92]}}',
        '{"user": {"name": "Bob", "scores": [78, 88, 91]}}',
        '{"user": {"name": "Charlie", "scores": [95, 93, 89]}}'
    ]
})

# Extract nested value
df.with_columns([
    pl.col('json_str').str.json_extract('$.user.name').alias('name'),
    pl.col('json_str').str.json_extract('$.user.scores[0]').alias('first_score')
])

# ============================================================================
# FILTERING ON JSON FIELDS
# ============================================================================

df = pl.DataFrame({
    'id': [1, 2, 3],
    'data': [
        {'name': 'Alice', 'age': 25, 'active': True},
        {'name': 'Bob', 'age': 30, 'active': False},
        {'name': 'Charlie', 'age': 35, 'active': True}
    ]
})

# Filter based on nested field
df.filter(pl.col('data').struct.field('age') > 28)
df.filter(pl.col('data').struct.field('active') == True)

# ============================================================================
# AGGREGATING JSON DATA
# ============================================================================

df = pl.DataFrame({
    'category': ['A', 'A', 'B', 'B'],
    'data': [
        {'value': 10, 'count': 5},
        {'value': 20, 'count': 3},
        {'value': 15, 'count': 7},
        {'value': 25, 'count': 2}
    ]
})

# Aggregate nested fields
df.group_by('category').agg([
    pl.col('data').struct.field('value').sum().alias('total_value'),
    pl.col('data').struct.field('count').mean().alias('avg_count')
])

# ============================================================================
# WORKING WITH ARRAY OF OBJECTS
# ============================================================================

df = pl.DataFrame({
    'id': [1, 2],
    'items': [
        [{'name': 'item1', 'price': 10}, {'name': 'item2', 'price': 20}],
        [{'name': 'item3', 'price': 15}, {'name': 'item4', 'price': 25}]
    ]
})

# Explode array of structs
df_exploded = df.explode('items')

# Extract fields after exploding
df_flat = (df_exploded
    .with_columns([
        pl.col('items').struct.field('name').alias('item_name'),
        pl.col('items').struct.field('price').alias('item_price')
    ])
    .drop('items')
)

# ============================================================================
# CONVERTING BETWEEN JSON AND STRUCT
# ============================================================================

# JSON string to struct
df = pl.DataFrame({'json_col': ['{"a": 1, "b": 2}', '{"a": 3, "b": 4}']})
df.with_columns(
    pl.col('json_col').str.json_decode().alias('struct_col')
)

# Struct to JSON string
df = pl.DataFrame({'struct_col': [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]})
df.with_columns(
    pl.col('struct_col').struct.json_encode().alias('json_col')
)

# ============================================================================
# HANDLING INVALID JSON
# ============================================================================

# Use try-except for error handling
try:
    df = pl.read_json('potentially_invalid.json')
except Exception as e:
    print(f"Error reading JSON: {e}")

# Parse JSON with error handling
df = pl.DataFrame({'json_str': ['{"valid": "json"}', 'invalid json', '{"also": "valid"}']})

# You'll need to handle invalid JSON before parsing
# Option 1: Filter out invalid JSON first
# Option 2: Use Python json module for validation

# ============================================================================
# PERFORMANCE TIPS FOR JSON
# ============================================================================

# 1. Use NDJSON format for large datasets (better streaming)
# 2. Parse JSON once and reuse the struct column
# 3. Use lazy evaluation with scan_ndjson for large files
# 4. Avoid repeated json_extract calls - parse once with json_decode
# 5. Consider converting to Parquet after parsing for better performance
# 6. Use unnest instead of multiple struct.field calls when extracting many fields

# Example: Efficient pipeline
result = (
    pl.scan_ndjson('large_file.ndjson')
    .with_columns(pl.col('json_col').str.json_decode().alias('parsed'))
    .unnest('parsed')
    .filter(pl.col('age') > 25)
    .collect()
)
```
