# Unity Catalog Governance Overview
Unity Catalog is the service responsible for tracking, securing, and sharing the data in Databricks. These areas are represented by the 4 main funtional areas:
- Data Access Controls: controling who has access to which data
- Data Access Audit: capturing and recording all access to data
- Data Lineage: Capture upstream sources and downstream consumers of data sets
- Data Discovery: Ability to serach for and discover authorized data.

### Data Governance of the Past
The warehousing workloads would be spread across multiple platforms across depengin on data ingestion, vs ML, vs AI, vs BI workloads. For example, most BI workloads the users are SQL deveoplers, but the ML prep and modelling teams have to build out data for python, spark, and R oriented workloads. This need spreads out the Governance of the same data sets across environments and tools making governance more difficult. Not to mention increased copies and synchronization needs of data.

For the last 2 item copies and synchronized data the cloud can help with the a bit. However the governance needs are still difficult, you have different clusters and cloud tools like Athena, Redshift, and EMR (plus more), so governance across all of these tools can be time consuming as well. To data they have no connecting permission setup without a well trained IAM and Cloudtrail IT professional.
