# Lakeflow Declarative Pipelines Performance
While DLT is a powerful tool for processing data incrementally, there are approaches the run faster in the respective use cases.

## Materialized Views
A materialized view is a method for storing a aggregate, ranked, or other type of computed query still as physical data. This is more effective than a view, because if multiple users injest the ended for there BI reports, or analysis, than the data is pre-computed 1-time. You can maintain the same pre-computed result set by dropping + recreating a table, but with a meterialzed view have the following advantages:
**Incremental Refresh Capabilities**
Materialized views can often refresh incrementally, updating only the rows that have changed in the underlying data. When you drop and recreate a table, you're always doing a full rebuild, which becomes increasingly expensive as data grows.

**Dependency Management**
Materialized views maintain metadata about their dependencies on base tables. The database can automatically invalidate or refresh them when underlying data changes. With drop/recreate patterns, you lose this automatic dependency tracking and must manage it manually.

**Concurrent Access**
Most databases allow queries against materialized views even during refresh operations (though this varies by implementation). Dropping and recreating a table creates a period where the data is completely unavailable.

**Storage Efficiency**
Materialized views can leverage database optimizations like compression and partitioning schemes that are specifically designed for read-heavy analytical workloads. They're also typically better integrated with the query optimizer.

**Transaction Safety**
Materialized view refreshes can be wrapped in transactions and rolled back if something goes wrong. The drop/recreate pattern is riskier - if the recreation fails, you've lost your data.

**Indexing and Statistics**
Indexes and query statistics on materialized views persist across refreshes. With drop/recreate, you lose these optimizations and must rebuild them each time.

You're right that conceptually they're similar - both are about maintaining a pre-computed result set. But materialized views provide a more robust, efficient, and database-integrated approach to this pattern, especially for production systems where uptime and performance matter.

## Joins
When join tables together with Declarative Table language you can do the following:
- Join Streaming Tables to Static Tables
- Join Streaming Table to Streaming Tables (output to a materialized view)
- Join Streaming Table to Streaming Tables (output to streaming table incrementally)

The correct method depends on the use case and can still require manuall work, if or when data is updated. For example, the static table could be update which would require rebuilding streaming tables. (Be careful not to loose data when rebuilding!)
