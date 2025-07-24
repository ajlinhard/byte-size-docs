# Change Data Capture (CDC)
Change Data Capture (CDC) is a data integration technique that identifies and captures changes made to data in a source system, then propagates those changes to target systems in near real-time or batch mode. CDC enables organizations to keep multiple systems synchronized without having to perform full data dumps or comparisons.

### Documentation
- [Databricks CDC Tutorial](https://docs.databricks.com/aws/en/dlt/tutorial-pipelines)
- [Databricks AUTO CDC](https://docs.databricks.com/aws/en/dlt/cdc)
  - [SQL AUTO CDC Syntax](https://docs.databricks.com/aws/en/dlt-ref/dlt-sql-ref-apply-changes-into)
  - [Python AUTO CDC Syntax](https://docs.databricks.com/aws/en/dlt-ref/dlt-python-ref-apply-changes)

## Important Components of CDC

**Change Detection Mechanism** forms the core of any CDC system. This component monitors the source database for modifications using various methods like database transaction logs, triggers, timestamps, or version numbers. Log-based CDC is considered the most efficient approach as it reads directly from the database's transaction log without impacting source system performance.

**Change Capture Process** extracts the identified changes and transforms them into a standardized format. This process must handle different types of operations (INSERT, UPDATE, DELETE) and maintain the sequence of changes to preserve data integrity.

**Change Delivery System** transports the captured changes to target systems. This component manages the communication protocols, handles network failures, ensures delivery guarantees, and may include buffering capabilities for handling peak loads.

**Metadata Management** tracks what changes have been processed, maintains schema information, and stores configuration details about source and target systems. This component is crucial for recovery scenarios and ensuring no changes are lost or duplicated.

**Transformation Engine** applies business rules and data transformations as changes flow from source to target. This may include data cleansing, format conversions, or enrichment processes.

## SCD1 vs SCD2: Key Differences

While Slowly Changing Dimensions (SCD) and CDC are related concepts in data warehousing, they serve different purposes. SCD strategies determine how to handle changes to dimensional data, while CDC is the mechanism for detecting and capturing those changes.

**SCD Type 1 (Overwrite)** replaces old values with new ones, maintaining no historical record of previous states. When a customer changes their address, the old address is completely overwritten with the new one. This approach keeps the data warehouse current but loses historical context. It's suitable for correcting errors or when historical values aren't needed for analysis.

**SCD Type 2 (Historical Tracking)** preserves historical data by creating new records for each change while maintaining references to previous versions. When a customer's address changes, the system creates a new record with the updated information and marks the previous record as historical, typically using effective dates or version numbers. This approach enables time-based analysis and trend identification but increases storage requirements and query complexity.

The choice between SCD1 and SCD2 depends on business requirements for historical data retention, storage constraints, and analytical needs. Many modern data warehouses implement hybrid approaches, using SCD1 for certain attributes and SCD2 for others based on their business significance.
