# Unity Catalog Access Patterns
When building out an organizations Databricks platform the access levels of each user/group is important. This can come into play for compliance, user training, data safety, department data ownership.

## Unity Catalog Isolation
There are permissions for each object type: MetaStores, Catalogs, Workspaces, as well as Schemas/Database, Tables, and View.
- MetaStores and Workspace permissions are accessable from the admin client.
- Other Object permissions can be down via the UI or with SQL commands.

<img width="1010" height="562" alt="image" src="https://github.com/user-attachments/assets/6b169ba3-d67a-485e-997e-45b22d78bce7" />

<img width="1309" height="652" alt="image" src="https://github.com/user-attachments/assets/0ebb05bb-8404-4cd1-8215-3814f85a624e" />

### Best Practices
- Separate Catalogs by Rsponsibility
  - Development Enviroment (dev, qa, prod)
  - Separate user groups by Business Unit (Finance, HR, Dev, Sales)
  - Sharing / Foreign Data (if you need to share input data with a client)
- Use Workspaces - Catalog Binding where required
  - Similare to above separate by Environemnt and/or Business Units.
- Create the minimum number of catalogs to meet your team's isolation and ownership needs.

<img width="1256" height="632" alt="image" src="https://github.com/user-attachments/assets/e2a73fb1-8691-4c93-acff-f65fc6f624f1" />

---
# Databricks Unity Catalog Permissions Cheatsheet

## Metastore Permissions

| Permission Name | Purpose | Concise Example |
|----------------|---------|----------------|
| **METASTORE_ADMIN** | Full administrative access to the metastore | Admin can create/delete catalogs, manage all permissions |
| **CREATE CATALOG** | Create new catalogs in the metastore | Data architect creates `prod_catalog` for production data |
| **USE CATALOG** | List and access catalogs within the metastore | Analyst can see available catalogs like `dev_catalog`, `staging_catalog` |

## Workspace Permissions

| Permission Name | Purpose | Concise Example |
|----------------|---------|----------------|
| **WORKSPACE_ADMIN** | Full administrative access to workspace | Admin manages all workspace resources and user permissions |
| **CREATE** | Create new objects in workspace (notebooks, jobs, etc.) | Data scientist creates notebooks and ML experiments |
| **USE** | Basic access to use workspace features | Business user can run existing dashboards and queries |

## Catalog Permissions

| Permission Name | Purpose | Concise Example |
|----------------|---------|----------------|
| **ALL PRIVILEGES** | Full control over catalog and all contained objects | Catalog owner has complete access to `finance_catalog` |
| **CREATE SCHEMA** | Create new schemas/databases within the catalog | Data engineer creates `raw_data` schema in catalog |
| **USE CATALOG** | List and access schemas within the catalog | Analyst can browse schemas in `marketing_catalog` |
| **BROWSE** | View catalog metadata without accessing data | Auditor can see catalog structure for compliance review |

## Schema/Database Permissions

| Permission Name | Purpose | Concise Example |
|----------------|---------|----------------|
| **ALL PRIVILEGES** | Full control over schema and all contained objects | Schema owner manages all tables in `customer_data` schema |
| **CREATE TABLE** | Create new tables within the schema | Data engineer creates `transactions` table in schema |
| **CREATE VIEW** | Create new views within the schema | Analyst creates `monthly_sales` view for reporting |
| **CREATE VOLUME** | Create new volumes for file storage | ML engineer creates volume for model artifacts |
| **USE SCHEMA** | List and access objects within the schema | Developer can see tables in `product_analytics` schema |
| **CREATE FUNCTION** | Create user-defined functions in the schema | Data scientist creates custom aggregation functions |

## Table Permissions

| Permission Name | Purpose | Concise Example |
|----------------|---------|----------------|
| **ALL PRIVILEGES** | Full control over the table | Table owner can read, write, and modify `users` table |
| **SELECT** | Read data from the table | Analyst queries `sales_data` table for monthly reports |
| **INSERT** | Add new rows to the table | ETL process inserts new records into `events` table |
| **UPDATE** | Modify existing rows in the table | Data steward updates customer addresses in `customers` table |
| **DELETE** | Remove rows from the table | Compliance team deletes expired records from `logs` table |
| **MODIFY** | Alter table structure (add/drop columns, etc.) | Data engineer adds new column to `products` table |

## View Permissions

| Permission Name | Purpose | Concise Example |
|----------------|---------|----------------|
| **ALL PRIVILEGES** | Full control over the view | View owner can modify and grant access to `sales_summary` view |
| **SELECT** | Query data through the view | Business user runs reports using `customer_360` view |
| **REFRESH** | Refresh materialized views | Scheduler refreshes `daily_metrics` materialized view |

## Volume Permissions

| Permission Name | Purpose | Concise Example |
|----------------|---------|----------------|
| **ALL PRIVILEGES** | Full control over the volume | Volume owner manages all files in `model_artifacts` volume |
| **READ FILES** | Read files stored in the volume | ML model loads training data from `datasets` volume |
| **WRITE FILES** | Write/upload files to the volume | Data pipeline saves processed files to `output` volume |
| **BROWSE** | List files and directories in the volume | Developer explores file structure in `logs` volume |

---

## Key Notes

- **Inheritance**: Permissions flow downward (metastore → catalog → schema → table/view)
- **ALL PRIVILEGES**: Grants all applicable permissions for that object type
- **Principal Types**: Permissions can be granted to users, service principals, or groups
- **Grant Syntax**: `GRANT <permission> ON <object> TO <principal>`
- **Revoke Syntax**: `REVOKE <permission> ON <object> FROM <principal>`
