# Unity Catalog Governance Overview
Unity Catalog is the service responsible for tracking, securing, and sharing the data in Databricks. These areas are represented by the 4 main funtional areas:
- Data Access Controls: controling who has access to which data
- Data Access Audit: capturing and recording all access to data
- Data Lineage: Capture upstream sources and downstream consumers of data sets
- Data Discovery: Ability to serach for and discover authorized data.

### Documentation and Tutorials
- [Unity Catalog - Open Source Project](https://www.unitycatalog.io/)
- [Databricks Unity Catalog](https://www.databricks.com/product/unity-catalog)
- [Databricks Academy - Data Governance with Unity Catalog](https://customer-academy.databricks.com/learn/courses/3144/data-management-and-governance-with-unity-catalog)

### Data Governance of the Past
The warehousing workloads would be spread across multiple platforms across depengin on data ingestion, vs ML, vs AI, vs BI workloads. For example, most BI workloads the users are SQL deveoplers, but the ML prep and modelling teams have to build out data for python, spark, and R oriented workloads. This need spreads out the Governance of the same data sets across environments and tools making governance more difficult. Not to mention increased copies and synchronization needs of data.

For the last 2 item copies and synchronized data the cloud can help with the a bit. However the governance needs are still difficult, you have different clusters and cloud tools like Athena, Redshift, and EMR (plus more), so governance across all of these tools can be time consuming as well. To data they have no connecting permission setup without a well trained IAM and Cloudtrail IT professional. Additionally, IAM and Cloudtrail do not govern the security of database, catalog, table, or column level details within a data engine.

## Data Intelligence Platform
#### **Activity**
Databricks AI, Delta Live Tables, Workflows, and Databricks SQL

#### Data Intelligence Engine
The ability to use generative AI to underdtand the semantics of the data in the platform.

#### **Security Provider**
Unified security layer for you data. The options are Unity Catalog (built-by Databricks) or Apache Hive (the native Spark catalog). Unity Catalog is the recomended tool with fantastic features and great integration with the other services in Databricks.

#### **Delta Lake**
The I/O of the plataform for the files generated and read during operations in Databricks. This is the Delta Lake open source projects. The data is also stored on the cloud provider(s) of your choice.

## Unity Catalog Features
- Unify Governance Across Clouds - fine-grained governance for data lake across cloud providers - base on the open standard ANSI SQL (aka grant and revoke statements)
- Unify Data and AI Assets - Centrally share, audit, secure, and manage all data types with on simple interface.
- Unify Existing Catalogs - works in concert with existing data, storage, and catalogs - no hard migration required
- Works well with other catalogs like Apache Hive and AWS Glue
- Open Source Project - as on early 2025 Unity Catalog is open source to make quicker advancements and help Databricks users avoid vendor lock-in.
- Integration with other data tools: Kafka (Confluent as well), Flink, DuckDB, Trino, Fivetran, etc.
- Data can be structured or unstructured, and stored using delta, iceberg, hudi, or basic file types (csv, orc, json, parquet)

![image](https://github.com/user-attachments/assets/5cdcfb38-5302-4ec0-9795-47327a39d76f)

---
# Unity Catalog Structure

![image](https://github.com/user-attachments/assets/f3c809f7-e4fd-4b99-beb0-1bcc5a26e52c)

## Metastore
A metastore is the location where the governing of your data begins. . The only users that can see the metastore is the administrator through the account console. A Metastore has 4 main building blocks:
1. Cloud Region
2. Cloud Storage: the S3 bucket or other cloud location to store files. The metastores info is split in 2 sections:
  - Control Plane: has all the metadata for the metastore and access control list
  - Cloud Storage: The data assets storage where the data files go.
3. Identity to access: the IAM Role or security entity for accessing the files/S3 location.
4. One or more workspace: A workspace is an environment of data assets. A metastore can point to one ore more for user groups and permissions.

**NOTE: A legacy Hive metastore also exists for hive catalogs. Only one per workspace.**

![image](https://github.com/user-attachments/assets/3d860f1e-5e71-4dbc-93b0-d0e7a459448e)

### **Unity Catalog has a 1:1 relationship with metastores at the account level.** 
Each Databricks account can have multiple metastores, but each metastore is independent and serves as the top-level container for that particular Unity Catalog instance.

The hierarchy works like this:
- **Account** (your Databricks organization)
  - **Metastore 1** (Unity Catalog instance for region/business unit A)
    - Catalogs → Schemas → Tables/Views
  - **Metastore 2** (Unity Catalog instance for region/business unit B)
    - Catalogs → Schemas → Tables/Views

Each metastore typically corresponds to a specific region or organizational boundary. Workspaces are then assigned to a metastore, and all the Unity Catalog governance (permissions, lineage, auditing) operates within that metastore's scope.

So rather than Unity Catalog controlling multiple metastores, it's more accurate to say that each metastore *is* a Unity Catalog instance. The multiple metastores exist at the account level to handle different regions, compliance requirements, or organizational divisions, but they operate independently of each other.

### Metastore Attached Entities
- Catalog - this is a namespace for bucketing out data. Note, this is not unity catalog itself. Unity Catalog can control mulitple catalogs under its domain. Underneath you can choose split data into different databases/schemas. 
- External Storage Access
- Query Federation
- Delta Sharing

### Catalogs
- Tables: for tabluar data whether structure or semi-structure.
- Views: for stored queries of data, with option of being materialized for faster processing.
- Volumes: for non-tabluar like images, json, pdf data. Can access a view the data from with in Databricks. Volumes are also Managed or External like tables.
- Functions: Stores standardized calculations you wish to do in SQL. The code
- Models: storing any ML models you have built-out for use.

**NOTE:** Hive catalog cannot handle Volume and Models.

![image](https://github.com/user-attachments/assets/2e1c80a7-b594-42c8-9f75-8d26eb536ea7)

### Lakehouse Federation
The ability to create a foreign catalog pointing to an external data source like postgreSQL, MSSQL, Snowflake, etc. This allows you to join the data in Databricks to the external sources.
- First create a connection pointing to the environment.
- The create a new catalog of type "foreign"

### Delta Sharing
Under the catalog explore, you can setup the ability to share notebooks or data with other platforms or applications. 
- You can share to platforms like Power BI, Tableau, Snowflake, etc.
- You can share tables, views, files, models, and more.
- Sharing cross-platform w/ Delta Sharing open protocol.
- Sharing data WITHOUT replication.
- Data is being pulled dynamically at the time its called.

### Other Unity Catalog Topics
- Feature Store: use any delta table in unity catalog with a primary key as a feature table for model training or inference.
- Vector Search Index: create auto-updating vector indees, managed by Unity Catalog to search through text for AI similarity searchs. Acting like a vector databse.

## Best Practices
- Lead with Managed Tables
  - They provide better performance and simplicity.
  - Managed tables uses Delta Lake which have tons of additional features: predictive IO, predictive optimization, time travel, CDC help.
  - Continued interoperability work and open APIs will reduce need for external tables.
  - You can undrop a table.
