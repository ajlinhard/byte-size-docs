# ORC File Overview
ORC (Optimized Row Columnar) files are a columnar storage format designed for big data processing, particularly in the Hadoop ecosystem. They're optimized for both storage efficiency and query performance.

Key characteristics of ORC files include:

**Columnar Storage**: Data is organized by columns rather than rows, which enables better compression and faster analytical queries since you only need to read the columns you're actually using.

**Advanced Compression**: ORC uses sophisticated compression algorithms including ZLIB, Snappy, and LZO, often achieving compression ratios of 75% or better compared to text formats.

**Built-in Indexing**: Files contain lightweight indexes, column statistics, and bloom filters that allow query engines to skip irrelevant data blocks entirely, dramatically speeding up queries.

**Schema Evolution**: ORC supports adding, dropping, and renaming columns without requiring data rewrites, making it flexible for evolving data schemas.

**ACID Properties**: When used with systems like Apache Hive, ORC supports ACID transactions for reliable data operations.

**Optimized for Analytics**: The format is specifically designed for read-heavy analytical workloads rather than transactional operations.

ORC files are commonly used with Apache Hive, Spark, Presto, and other big data tools. They're particularly valuable when you need to store and query large datasets efficiently, offering significant performance improvements over traditional row-based formats like CSV or even other columnar formats in many scenarios.

The format strikes a good balance between storage efficiency, query performance, and ecosystem compatibility in the big data world.
