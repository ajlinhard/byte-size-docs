# Delta vs. Parquet Format
The file structure differences between Delta and Parquet as default formats are quite significant:

## Parquet Default Structure

**Standard Hive/Parquet table:**
```
my_table/
├── part-00000-uuid.snappy.parquet
├── part-00001-uuid.snappy.parquet
├── part-00002-uuid.snappy.parquet
└── _SUCCESS
```

**With partitioning:**
```
my_partitioned_table/
├── year=2023/
│   ├── month=01/
│   │   ├── part-00000-uuid.snappy.parquet
│   │   └── part-00001-uuid.snappy.parquet
│   └── month=02/
│       └── part-00000-uuid.snappy.parquet
└── _SUCCESS
```

## Delta Lake Structure

**Delta table structure:**
```
my_delta_table/
├── _delta_log/
│   ├── 00000000000000000000.json
│   ├── 00000000000000000001.json
│   ├── 00000000000000000002.json
│   └── _last_checkpoint
├── part-00000-uuid.snappy.parquet
├── part-00001-uuid.snappy.parquet
└── part-00002-uuid.snappy.parquet
```

**With partitioning:**
```
my_delta_partitioned_table/
├── _delta_log/
│   ├── 00000000000000000000.json
│   ├── 00000000000000000001.json
│   └── _last_checkpoint
├── year=2023/
│   └── month=01/
│       ├── part-00000-uuid.snappy.parquet
│       └── part-00001-uuid.snappy.parquet
└── year=2023/
    └── month=02/
        └── part-00000-uuid.snappy.parquet
```

## Key Structural Differences

| Aspect | Parquet Default | Delta Lake |
|--------|----------------|------------|
| **Transaction Log** | ❌ None | ✅ `_delta_log/` directory |
| **Metadata Storage** | Only in Hive Metastore | Hive Metastore + Delta log |
| **Version History** | ❌ No versioning | ✅ JSON files track versions |
| **File Tracking** | Directory listing | Transaction log entries |
| **Schema Evolution** | Manual metastore updates | Automatic in transaction log |
| **Checkpoints** | ❌ None | ✅ `_last_checkpoint` files |

## Transaction Log Contents (Delta)

**Example `00000000000000000000.json`:**
```json
{
  "commitInfo": {
    "timestamp": 1640995200000,
    "operation": "WRITE",
    "operationParameters": {"mode": "ErrorIfExists"}
  }
}
{
  "metaData": {
    "id": "uuid-here",
    "format": {"provider": "parquet"},
    "schema": "{\"type\":\"struct\",\"fields\":[...]}"
  }
}
{
  "add": {
    "path": "part-00000-uuid.snappy.parquet",
    "size": 1234,
    "modificationTime": 1640995200000,
    "dataChange": true
  }
}
```

## File Management Differences

**Parquet (Standard):**
- Files are directly managed by Spark/Hive
- Overwrites replace entire directory contents
- No built-in cleanup mechanism
- Schema stored only in Hive Metastore

**Delta Lake:**
- Files tracked in transaction log
- Old files remain until explicitly cleaned up
- `VACUUM` command removes old files
- Schema evolution tracked in log
- Atomic operations via log entries

## Practical Implications

**Storage:**
- Delta tables use slightly more storage due to transaction log
- Old file versions remain until `VACUUM` is run
- Parquet tables immediately remove old files on overwrite

**Performance:**
- Delta can skip files using transaction log statistics
- Parquet relies on directory listing and file metadata
- Delta provides better query optimization through log statistics

**Consistency:**
- Delta guarantees ACID transactions
- Parquet can have consistency issues with concurrent operations

The main takeaway is that Delta Lake adds a sophisticated metadata layer (`_delta_log`) on top of the same underlying Parquet files, providing transactional guarantees and advanced features that standard Parquet tables lack.
