# Spark File Loading Options Cheatsheet

## Schema and Data Type Options

| Option Name | Purpose | File Types | Example |
|-------------|---------|------------|---------|
| `schema` | Define explicit schema | CSV, JSON | `schema "name STRING, age INT, salary DECIMAL(10,2)"` |
| `inferSchema` | Auto-detect column types | CSV, JSON | `inferSchema "true"` |
| `header` | First row contains column names | CSV | `header "true"` |
| `timestampFormat` | Custom timestamp parsing | CSV, JSON | `timestampFormat "yyyy-MM-dd HH:mm:ss"` |
| `dateFormat` | Custom date parsing | CSV, JSON | `dateFormat "MM/dd/yyyy"` |
| `columnNameOfCorruptRecord` | Store unparseable records | CSV, JSON | `columnNameOfCorruptRecord "_corrupt_record"` |

## File Reading Behavior

| Option Name | Purpose | File Types | Example |
|-------------|---------|------------|---------|
| `path` | File/directory location | All | `path "/data/sales/*.csv"` |
| `pathGlobFilter` | Filter files by pattern | All | `pathGlobFilter "*.csv"` |
| `recursiveFileLookup` | Search subdirectories | All | `recursiveFileLookup "true"` |
| `modifiedBefore` | Only files modified before date | All | `modifiedBefore "2024-01-01T00:00:00"` |
| `modifiedAfter` | Only files modified after date | All | `modifiedAfter "2024-01-01T00:00:00"` |
| `maxFilesPerTrigger` | Limit files per batch | All (streaming) | `maxFilesPerTrigger "100"` |

## CSV-Specific Options

| Option Name | Purpose | File Types | Example |
|-------------|---------|------------|---------|
| `sep` | Field separator | CSV | `sep ";"` |
| `delimiter` | Alternative to sep | CSV | `delimiter "\t"` |
| `quote` | Quote character | CSV | `quote "'"` |
| `escape` | Escape character | CSV | `escape "\\"` |
| `comment` | Comment line prefix | CSV | `comment "#"` |
| `nullValue` | String representing null | CSV | `nullValue "NA"` |
| `emptyValue` | String representing empty | CSV | `emptyValue ""` |
| `ignoreLeadingWhiteSpace` | Trim leading spaces | CSV | `ignoreLeadingWhiteSpace "true"` |
| `ignoreTrailingWhiteSpace` | Trim trailing spaces | CSV | `ignoreTrailingWhiteSpace "true"` |
| `multiLine` | Handle multi-line records | CSV | `multiLine "true"` |
| `encoding` | Character encoding | CSV | `encoding "UTF-8"` |

## JSON-Specific Options

| Option Name | Purpose | File Types | Example |
|-------------|---------|------------|---------|
| `multiLine` | Single JSON object per file | JSON | `multiLine "true"` |
| `allowComments` | Allow // comments in JSON | JSON | `allowComments "true"` |
| `allowUnquotedFieldNames` | Allow unquoted field names | JSON | `allowUnquotedFieldNames "true"` |
| `allowSingleQuotes` | Allow single quotes | JSON | `allowSingleQuotes "true"` |
| `allowNumericLeadingZeros` | Allow leading zeros | JSON | `allowNumericLeadingZeros "true"` |
| `allowBackslashEscapingAnyCharacter` | Allow \\ escaping | JSON | `allowBackslashEscapingAnyCharacter "true"` |
| `primitivesAsString` | Parse all as strings | JSON | `primitivesAsString "true"` |
| `dropFieldIfAllNull` | Remove null-only fields | JSON | `dropFieldIfAllNull "true"` |

## Error Handling Options

| Option Name | Purpose | File Types | Example |
|-------------|---------|------------|---------|
| `mode` | Error handling strategy | CSV, JSON | `mode "PERMISSIVE"` (PERMISSIVE, DROPMALFORMED, FAILFAST) |
| `badRecordsPath` | Save bad records location | CSV, JSON | `badRecordsPath "/tmp/bad_records"` |
| `maxMalformedLogPerPartition` | Max logged bad records | CSV, JSON | `maxMalformedLogPerPartition "20"` |
| `ignoreCorruptFiles` | Skip corrupt files | All | `ignoreCorruptFiles "true"` |
| `ignoreMissingFiles` | Skip missing files | All | `ignoreMissingFiles "true"` |

## Parquet-Specific Options

| Option Name | Purpose | File Types | Example |
|-------------|---------|------------|---------|
| `mergeSchema` | Merge schemas across files | Parquet | `mergeSchema "true"` |
| `datetimeRebaseMode` | Handle date rebasing | Parquet | `datetimeRebaseMode "CORRECTED"` |
| `int96RebaseMode` | Handle int96 timestamps | Parquet | `int96RebaseMode "CORRECTED"` |

## Delta Lake-Specific Options

| Option Name | Purpose | File Types | Example |
|-------------|---------|------------|---------|
| `timestampAsOf` | Time travel to timestamp | Delta | `timestampAsOf "2024-01-01 00:00:00"` |
| `versionAsOf` | Time travel to version | Delta | `versionAsOf "5"` |
| `ignoreDeletes` | Skip deleted files | Delta | `ignoreDeletes "true"` |
| `ignoreChanges` | Skip change files | Delta | `ignoreChanges "true"` |
| `startingTimestamp` | Streaming start time | Delta | `startingTimestamp "2024-01-01"` |
| `startingVersion` | Streaming start version | Delta | `startingVersion "10"` |

## Performance Options

| Option Name | Purpose | File Types | Example |
|-------------|---------|------------|---------|
| `maxColumns` | Max columns to parse | CSV, JSON | `maxColumns "20000"` |
| `maxCharsPerColumn` | Max chars per column | CSV, JSON | `maxCharsPerColumn "1000000"` |
| `samplingRatio` | Sample ratio for schema inference | JSON | `samplingRatio "0.1"` |
| `multiline` | Better performance for large JSON | JSON | `multiline "false"` |
| `lineSep` | Line separator override | CSV, JSON | `lineSep "\n"` |

## Common Usage Patterns

### Basic CSV Loading
```sql
CREATE OR REPLACE TEMPORARY VIEW csv_data
USING CSV
OPTIONS (
  path "/data/sales.csv",
  header "true",
  inferSchema "true",
  mode "PERMISSIVE"
)
```

### Robust JSON Loading
```sql
CREATE OR REPLACE TEMPORARY VIEW json_data
USING JSON
OPTIONS (
  path "/data/events/*.json",
  multiLine "true",
  timestampFormat "yyyy-MM-dd'T'HH:mm:ss.SSSX",
  badRecordsPath "/tmp/bad_json"
)
```

### Parquet with Schema Evolution
```sql
CREATE OR REPLACE TEMPORARY VIEW parquet_data
USING PARQUET
OPTIONS (
  path "/data/warehouse/sales/",
  mergeSchema "true",
  recursiveFileLookup "true"
)
```

### Delta Time Travel
```sql
CREATE OR REPLACE TEMPORARY VIEW delta_snapshot
USING DELTA
OPTIONS (
  path "/data/delta/sales/",
  timestampAsOf "2024-01-01 00:00:00"
)
```
