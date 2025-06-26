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
