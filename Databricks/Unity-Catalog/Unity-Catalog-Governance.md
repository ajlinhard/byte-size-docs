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

