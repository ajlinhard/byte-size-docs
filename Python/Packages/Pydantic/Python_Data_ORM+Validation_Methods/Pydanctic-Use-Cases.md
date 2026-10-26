
# General Rule for Pydantic
**For Boundary Crossings, NOT for bulk processing**
Pydantic is built to check that each individual record is well-formed as it crosses a boundary: an API request, a message from a queue, a config file, a response from another service. Bulk pipelines and analysis work on whole sets of data at once, and creating one Pydantic object per row costs time and memory without telling you much that set-level checks can't.

The same goes for the ORM. Loading 5 million rows as `Order` objects and changing them one at a time is far slower than one set-based statement. In bulk work you usually skip both layers:

```python
# Instead of loading rows and mutating them in a loop:
session.execute(
    update(Order)
    .where(Order.status == "pending", Order.created_at < cutoff)
    .values(status="cancelled")
)

# Bulk insert with Core: plain dicts, no ORM objects, no Pydantic
session.execute(insert(Order), list_of_dicts)
```

For analysis, the tools are SQL itself, pandas, polars, or DuckDB, which operate on whole columns rather than individual objects.

**Where Pydantic still helps in pipelines**

The rule isn't "never in bulk work". It's "use it at the edges", and a pipeline has edges too.

- **Ingesting external data.** Pulling records from a vendor API, CSV drops, or JSON files is a boundary, and bad records are common there. Validating each one at intake, and routing failures to a quarantine table instead of crashing the job, is a good use of Pydantic. Pydantic v2's validation core is written in Rust, so this is often fast enough for thousands to low millions of records. `TypeAdapter(list[RecordIn]).validate_json(raw_bytes)` validates a whole payload in one call.
- **Pipeline configuration.** Job parameters, connection settings, and run options benefit from Pydantic, and `pydantic-settings` exists for exactly this.
- **Output contracts.** If the pipeline publishes summary records to another system, a schema for that output documents and enforces the contract.

**For in-pipeline data quality, use column-level tools**

When the data is already in a DataFrame or table, check it as a whole rather than row by row:

- **Database constraints** (`NOT NULL`, `CHECK`, foreign keys) are still your last line of defense, even for bulk loads.
- **Pandera** declares a schema for pandas or polars DataFrames and checks it on whole columns at once.
- **Polars and Arrow schemas** enforce types when you load the data.
- **Plain SQL checks**, such as `SELECT count(*) WHERE total_amount < 0`, run as a step in the pipeline.

**Rough guide**

| Situation | Tool |
|---|---|
| One request, message, or record in or out | Pydantic + ORM row |
| Multi-step change to a few related rows | ORM row inside one transaction |
| Ingesting messy external records | Pydantic per record, quarantine failures |
| Changing many rows by the same rule | Set-based SQL (`update`/`insert` in Core) |
| Analysis and aggregation | SQL, pandas/polars, DuckDB |
| Data quality on a whole table or frame | DB constraints, Pandera, SQL checks |

So your instinct is right. Pydantic and ORM rows are for working with individual records, and bulk work is better done with tools that operate on whole sets.
