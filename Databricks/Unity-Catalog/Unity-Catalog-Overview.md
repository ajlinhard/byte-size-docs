# Unity Catalog Overview

### Documentation and Tutorials
- [Databricks Unity Catalog - Home Page]()
- [Unity Catalog Open Source]()
- [Unity Catalog + Iceberg](https://www.databricks.com/blog/announcing-full-apache-iceberg-support-databricks)

## Unity Catalog as a Metastore
In Unity Catalog, the **metastore** is the foundational component that serves as the top-level container for all metadata and governance information. It's essentially the central repository that stores and manages metadata about your data assets, security policies, lineage information, and access controls.

## Key aspects of the metastore:

- **Metadata storage**: Stores information about catalogs, schemas, tables, columns, data types, and relationships
- **Security enforcement**: Manages access control lists (ACLs), permissions, and governance policies
- **Lineage tracking**: Maintains data lineage and audit logs
- **Regional boundary**: Typically deployed per region for compliance and performance reasons
- **Workspace association**: Multiple Databricks workspaces can be attached to a single metastore

## Other key components of Unity Catalog:

**1. Catalogs**
- Top-level containers for organizing data assets
- Logical grouping mechanism for schemas and tables

**2. Schemas (Databases)**
- Second-level containers within catalogs
- Group related tables, views, and functions

**3. Tables and Views**
- Actual data objects containing your datasets
- Support for managed tables, external tables, and views

**4. Volumes**
- Storage locations for non-tabular data (files, images, etc.)
- Can be managed or external volumes

**5. Functions**
- User-defined functions (UDFs) and stored procedures
- Shared across workspaces attached to the metastore

**6. External Locations**
- References to external storage systems (S3, ADLS, GCS)
- Define paths that Unity Catalog can access

**7. Storage Credentials**
- Authentication mechanisms for accessing external storage
- Securely store cloud provider credentials

**8. Data Lineage and Audit Logs**
- Track data movement and transformations
- Maintain compliance and governance records

**9. Delta Sharing**
- Secure data sharing capabilities with external organizations
- Share data without copying or moving it

The metastore acts as the central nervous system that coordinates all these components, ensuring consistent governance, security, and metadata management across your entire data platform.

---
# Data Lineage
Databricks Unity Catalog does provide **column-level lineage** for datasets, in addition to data set level. This is one of Unity Catalog's key features and has been generally available since its release.

## Key aspects of column-level lineage in Databricks:

**Automatic capture**: Unity Catalog automatically captures runtime data lineage across queries run on Databricks, and lineage is supported for all languages and is captured down to the column level.

**Multi-language support**: Lineage is supported for all languages (SQL, Python, Scala, and R) and works across different execution modes including batch and streaming.

**Real-time visualization**: To view column-level lineage, click a column in the graph to show links to related columns. The lineage can be visualized in Catalog Explorer in near real-time.

**Cross-workspace aggregation**: Lineage is aggregated across all workspaces attached to a Unity Catalog metastore. This means that lineage captured in one workspace is visible in any other workspace that shares that metastore.

**Unified view**: With Unity Catalog, users can now see both column and table lineage in a single lineage graph, giving users a better understanding of what a particular table or column is made up of and where the data is coming from.

## Requirements and limitations:

- Tables must be registered in Unity Catalog
- Because lineage is computed on a one-year rolling window, lineage collected more than one year ago is not displayed
- Specific runtime requirements: Column lineage tracking for Lakeflow Declarative Pipelines workloads requires Databricks Runtime 13.3 LTS or above
- Security is built-in: users can only see lineage for data they have permissions to access

The column-level lineage capability makes Unity Catalog particularly powerful for compliance requirements like GDPR, impact analysis, and root cause analysis when data quality issues occur.

Based on my research, I can provide you with a comprehensive answer about Iceberg and Unity Catalog system tables.

---
# Delta Sharing
When you need to share data between cloud regions, organizations, or applications (Snowflake, Tableau, AWS Redshift, etc) use the Delta Sharing feature in Databricks. The features is based off the open soruce Delta Sharing Protocol. In addition to built-in sharing providers like FiveTran have connectors setup to bring data into and out of Databricks.

When you set up Delta Sharing in Databricks, you configure sharing at the Unity Catalog metastore level. This means:
- The metastore acts as the top-level container for all shared data
- You can then share specific catalogs, schemas, and tables from within that metastore
- Recipients connect to the metastore and can access the shared objects you've granted them permissions to
<img width="1277" height="661" alt="image" src="https://github.com/user-attachments/assets/db743ca6-b783-4f32-af8d-1c553263a516" />

### Best Practices
- Use a Single Cloude Region per MetasStore as well as for SDLC and Business Unit scopes.
- Use Databricks-to-Databricks Delta Sharing between cloud providers + regions. Better performance.
- If a MetaStore will have delta sharing think through compliance, user groups, and access patterns.

---
# Current State of Unity Catalog System Tables

Unity Catalog provides system tables for operational data including audit logs, billable usage, and lineage, but these system tables remain the same regardless of whether you're using Delta Lake, Iceberg, or other table formats.

The existing Unity Catalog system tables include:
- `system.access.audit` - Audit logs
- `system.access.table_lineage` - Table-level lineage 
- `system.access.column_lineage` - Column-level lineage
- `system.billing.usage` - Billing and usage data

## How Iceberg Works with Unity Catalog

When you enable Iceberg reads on Delta tables (via UniForm), Unity Catalog adds metadata fields to track metadata generation status, but these appear in table properties rather than as new system tables. You can view these via:
- `DESCRIBE EXTENDED table_name` (shows Delta Uniform Iceberg section)
- Catalog Explorer in the UI
- REST API calls

## Lineage and Governance Remain Unified

Unity Catalog provides fine-grained access controls, lineage, and auditing on all data, across catalogs and regardless of format. This means:

- **Iceberg tables managed by Unity Catalog** use the same system tables for lineage and audit tracking as Delta tables
- **Foreign Iceberg tables** (from external catalogs like AWS Glue) can be federated into Unity Catalog and will appear in the same system tables
- Lineage is captured down to the column level and stored in the existing lineage system tables

## Key Takeaway

Unity Catalog's system table architecture is **format-agnostic**. Whether you're using Delta Lake, Iceberg (via UniForm), or native Iceberg tables, they all use the same underlying system tables for governance, lineage, and auditing. Unity Catalog breaks format silos through open standards while maintaining a unified metadata layer.

The power comes from Unity Catalog's ability to provide consistent governance across multiple table formats without requiring separate system tables for each format.
