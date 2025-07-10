# Delta Lake Overview
Delta Lake is an open-source data management platform originally created by Databricks. The service is very helpful for large amounts of data as well as incremental processing of the data.
- It enhances data operations and analytics
  - This is accomplished by tracking versions of the data and storing it all in one place.
- The system leveraged standard data formats.
  - Specifically, it is an optimized version of parquet files.
- Optimized for Cloud Storage (S3, and Google/Azure equivalents)
  - This was done because its cheap (vs Block Storage), highly available, durable, and effectively infinitely scalable.
- Built for efficient metadata handling.
  - Solves the problem of point queries.
  - Don't have to lock your data into traditional database management systems which do not scale as well. Databricks separates compute and storage.
- Single copy of your data.
 
  This is the foundation of the Databricks Data Lake house and aids in the performance speed increase of Databricks. The viability and usability of the data increases with the Delta Lake format.

# ACID Transactions (Atomicity, Consisency, Isolation, and Durability)
The base Apache Spark does not have ACID transactions. It has eventually, consistency which is a different concept. Typically, these are only available in traditional Relational Database Management systems. However, Databricks Runtime and Apache Spark combine with Delta Lake is ACID compliant. Delta Lake extends Apache Spark to provide ACID transaction guarantees that standard Spark lacks.

Here's how Delta Lake achieves ACID compliance:

**Atomicity**: Delta Lake ensures that operations either complete entirely or fail completely. Multi-part operations like complex ETL jobs are treated as single atomic units.

**Consistency**: Delta Lake maintains data consistency through schema enforcement and validation. It prevents writes that would violate table schemas or constraints.

**Isolation**: Multiple concurrent operations are isolated from each other using optimistic concurrency control. Delta Lake uses a transaction log to coordinate concurrent reads and writes, ensuring that concurrent operations don't interfere with each other.

**Durability**: Once a transaction is committed, Delta Lake persists the changes durably to storage. The transaction log provides a reliable record of all changes.

Delta Lake implements these ACID properties through several key mechanisms:

- **Transaction Log**: A centralized log that records all changes to the table in order
- **Optimistic Concurrency Control**: Allows multiple writers while detecting and resolving conflicts
- **Versioning**: Maintains multiple versions of data files, enabling time travel and rollback capabilities
- **Schema Evolution**: Supports safe schema changes while maintaining consistency

This makes Delta Lake suitable for use cases requiring strong consistency guarantees, such as financial data processing, regulatory compliance, and scenarios where data accuracy is critical. Standard Apache Spark without Delta Lake does not provide these ACID guarantees.
![image](https://github.com/user-attachments/assets/54a5a492-96bf-4cf7-81c4-c3c9f38e23a9)

# Medallion Architecture (aka Multi-hop)
Bronze is the Raw data storage which is not altered, or adjusted at all.
Silver is the transformation, hygiene and column additions.
Gold is the aggregates, joined, or normalized data.
![image](https://github.com/user-attachments/assets/add4492a-b630-41dc-8d23-b4150ffe58ff)

### Bronze Layer
- Typically just a raw copy of the ingested data.
  - The reason to leave it raw, aka no transforms or deduplication is to avoid back-pressure.
- Replaces traditional data lakes.
- Provides efficient storage and querying of full, unprocessed history of data.
  - This allows for an accurate review and study of all data created. Solve ingest issues, or gather even more insights from transactions.

### Silver Layer
- Reduce data storage complexity, latency, and redundancy
- Optimizes ETL throughput and analytic query performance.
- Tons of transformation: data type casting, null-handing, data mining
- Preserves grain of original data (without aggregation)
- Eliminates duplicated
- Enforce production schema
- Data quality check, corrupt data quarantined

### Gold Layer
- Powers ML applications, reporting, dashboards, and ad hoc analytics
- Refined views of data, typlically with aggregations
- Reduces strain on production systems
- Optimizes query perfomance for business-critical data

## Metastore
A metastore contains all the catalogs, schemas(databases), tables, views , functions, etc in your system. A workspace is assigned a Metastore to work on/from. The databricks admin sets this up.
![image](https://github.com/user-attachments/assets/d8ab9b15-dff3-479c-a322-fdf883422b58)

### Catalog
A catalog serves as a logical grouping mechanism that helps organize related databases (schemas) and their associated data objects. For example, you might have separate catalogs for different business units, environments (dev/staging/prod), or data domains.

### Schemas(database)
Unlike the tradional RDBMS the schema is essentially the same as the database. You may orgainze the schema for different departments or sets of data within your company, but this is logical separator for the data within a catalog.

### Tables
There are managed table sand external tables. 
![image](https://github.com/user-attachments/assets/c41523a4-dd60-43ba-8ba9-3b2a6f1d268b)
<br>
**Managed tables** are stored in the default S3 storage location configured for the meta store. <br>
**External tables** are stored in a configured addition S3 location with separate credentials setup to interact with location.
<img width="1283" height="557" alt="image" src="https://github.com/user-attachments/assets/a551e159-7d4c-4f40-adbe-6c81366652f2" />


### Views
Temporary Views
Global Temporary Views
Regular View

### Functions
A set of operation which returns a scalar value or a set of rows. (tabular). The function exists between sessions of process, verse function used in a notebook.

---
## Liquid Clustering
Liquid Clustering introduced around 2023 was designed to help with query efficency where traditional partitionind and z-ordering tend to start to hit limitations. Liquid clustering is helpful in the scenarios listed in the following figure. More info is available on the detailed [Liquid Clustering Page]
### Scenarios that benefit from Liquid Clustering
- Tables often filtered by high cardinality columns.
- Tables with significant skew in data distribution.
- Tables that grow quickly and require maintenance and tuning effort.
- Tables with concurrent write requirements.
- Tables with access patterns that change over time.
- Tables where a typical partition key could leave the table with too many or too few partitions.

## Deletion Vectors
Deletion Vectors are used to optimize changed to your data. Before when changing data in a table using databrick/spark a full file rewrite would be required. With deletion vectors and photon now deletes, merges, and updates are write to deletion vector files. Then photon leverages deletion vector files for faster queries using predictive I/O

## Predictive I/O
- Automates Optimize and Vacuum operations
- Based on Databricks' years of experience in building large AI/ML systems
- Makes the lakehouse a smarter data warehouse
- Works to have the best cost/benefit possible
- Uses ML to determine the most efficient access pattern to read data
- Leverages deletion vectors to accelerate updates by reducing the frequency of full file rewrites

