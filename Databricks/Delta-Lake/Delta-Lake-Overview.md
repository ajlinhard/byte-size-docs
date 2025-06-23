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
The base Apache Spark does not have ACID transactions. It has eventually, consistency which is a different concept. Typically, these are only available in traditional Relational Database Management systems.
![image](https://github.com/user-attachments/assets/54a5a492-96bf-4cf7-81c4-c3c9f38e23a9)


# Medallion Architecture
Bronze is the Raw data storage which is not altered, or adjusted at all.
Silver is the transformation, hygiene and column additions.
Gold is the aggregates, joined, or normalized data.
![image](https://github.com/user-attachments/assets/add4492a-b630-41dc-8d23-b4150ffe58ff)

## Metastore
A metastore contains all the catalogs, schemas(databases), tables, views , functions, etc in your system. A workspace is assigned a Metastore to work on/from. The databricks admin sets this up.
![image](https://github.com/user-attachments/assets/d8ab9b15-dff3-479c-a322-fdf883422b58)

### Catalog
A catalog serves as a logical grouping mechanism that helps organize related databases (schemas) and their associated data objects. For example, you might have separate catalogs for different business units, environments (dev/staging/prod), or data domains.

### Schemas(database)
Unlike the tradional RDBMS the schema is essentially the same as the database. You may orgainze the schema for different departments or sets of data within your company, but this is logical separator for the data within a catalog.

### Tables
There are managed table sand external tables. 
**Managed tables** are stored in the default S3 storage location configured for the meta store.
**External tables** are stored in a configured addition S3 location with separate credentials setup to interact with location.
![image](https://github.com/user-attachments/assets/c41523a4-dd60-43ba-8ba9-3b2a6f1d268b)

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

