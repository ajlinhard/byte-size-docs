# Databricks Unity Catalog: Complete Guide from Beginner to Advanced

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Features](#core-features)
4. [Governance Models](#governance-models)
5. [Beginner Level Topics](#beginner-level-topics)
6. [Intermediate Level Topics](#intermediate-level-topics)
7. [Advanced Level Topics](#advanced-level-topics)
8. [Use Cases](#use-cases)
9. [Best Practices](#best-practices)

---

## Overview

<cite index="2-1">Unity Catalog delivers AI-powered curation of your most trusted data and AI assets, including tables, dashboards and models, with shared business context in one unified experience.</cite> <cite index="6-1">Unity Catalog is the unified governance layer for data and AI built into Databricks. When enabled for a workspace, Unity Catalog operates beneath every data and AI interaction in your workspaces automatically: enforcing access control when you query a table or call a model, tracking lineage as data and AI assets are used, logging activity for auditing, and more.</cite>

### Key Points:
- Centralized governance layer for data and AI assets
- Enforces access control automatically
- Provides lineage tracking
- Enables audit logging
- Cross-workspace and cross-cloud support
- <cite index="7-1">Automatically enabled for all new Databricks workspaces created since November 2023</cite>

---

## Architecture

### 1. Hierarchical Structure

<cite index="10-1">Data and AI assets such as tables, views, volumes, functions, models, and services (model services and MCP services) follow a three-level namespace (catalog.schema.object).</cite>

```
Metastore (Regional)
├── Catalog 1
│   ├── Schema 1
│   │   ├── Table
│   │   ├── View
│   │   ├── Volume
│   │   └── Function
│   └── Schema 2
├── Catalog 2
└── Catalog 3
```

### 2. Metastore Architecture

<cite index="5-1">The Metastore contains all the metadata of the Unity Catalog objects within a cloud provider and within a region. The Metastore Admin can create catalogs, manage workspace-catalog assignments, user groups, create objects such as shares, clean rooms, catalogs.</cite>

<cite index="1-1">Use one metastore per region as the default pattern for operational simplicity. Assign workspaces in the same region to the same metastore.</cite>

### 3. Storage Architecture

Unity Catalog supports three types of objects:
- **Managed Tables**: Unity Catalog handles both governance and storage lifecycle
- **External Tables**: Unity Catalog handles governance only; user manages storage
- **Foreign Objects**: References to objects in other systems

---

## Core Features

### 1. Unified Governance
- Single permission model using ANSI SQL
- Consistency across workspaces and clouds
- Account-level identity management

### 2. Access Control Models

<cite index="7-1">Access modes were renamed in 2024: Shared is now Standard, Single User is now Dedicated.</cite>

- **Standard (formerly Shared)**: Multi-user clusters with fine-grained access control
- **Dedicated (formerly Single User)**: Single-principal workloads (ML jobs, pipelines)

### 3. Fine-Grained Access Control

<cite index="11-1">Unity Catalog provides two related mechanisms for row-level and column-level access control: ABAC policies attach at the catalog or schema level and apply automatically to tables and columns based on governed tags.</cite>

### 4. Advanced Security Features

<cite index="13-1">ABAC policies are Unity Catalog's dynamic access control model. It controls access based on the attributes of the data, so a single policy can cover many matching tables instead of each one being configured individually.</cite>

### 5. Data Sharing

<cite index="7-1">Delta Sharing is an open protocol built into Unity Catalog for securely sharing data and AI assets across clouds, regions and organizations. Recipients don't need to be on Databricks. Data is shared in open formats without ETL or data duplication.</cite>

### 6. Open Table Format Support

<cite index="7-1">As of 2025, Unity Catalog supports Apache Iceberg natively, including as a managed table format. It also supports the Iceberg REST Catalog API, so Iceberg-compatible clients can query data governed by Unity Catalog directly.</cite>

### 7. System Tables

<cite index="7-1">System tables are operational data tables exposed by Unity Catalog that contain audit logs, billable usage data and lineage information. They're generally available (GA) and queryable from Databricks SQL using the system catalog.</cite>

---

## Governance Models

### 1. Centralized Governance
<cite index="1-1">Each business unit or domain operates in a different business boundary, but all units fall under the same operational boundary that governs all data and AI assets (multi-tenancy). A single platform or data governance team controls all data assets, policies, and access.</cite>

### 2. Decentralized Governance
<cite index="1-1">Each business unit or domain has an independent business and operational boundary (meaning it has its own tenant). Governance is delegated to each business unit to define and enforce its own policies independently with minimal central oversight.</cite>

### 3. Catalog Design Patterns

<cite index="3-1">Environment-based catalogs (dev, staging, prod) support environment promotion workflows and prevent accidental production changes. Domain-based catalogs (sales, marketing, finance, engineering) align with data mesh architectures and domain ownership. Hybrid catalogs combine environment and domain patterns (for example, sales_prod, sales_dev, finance_prod, finance_dev).</cite>

---

## Beginner Level Topics

### Topic 1: Setting Up Your First Catalog

#### SQL Example:
```sql
-- Create a catalog
CREATE CATALOG IF NOT EXISTS sales_catalog;

-- Create a schema within the catalog
CREATE SCHEMA IF NOT EXISTS sales_catalog.transactions;

-- Create a simple managed table
CREATE TABLE IF NOT EXISTS sales_catalog.transactions.orders (
    order_id INT,
    customer_id INT,
    order_date DATE,
    total_amount DECIMAL(10, 2),
    status STRING
)
USING DELTA;

-- View catalog structure
SHOW CATALOGS;
SHOW SCHEMAS IN sales_catalog;
SHOW TABLES IN sales_catalog.transactions;
```

#### Python Example:
```python
from pyspark.sql.types import StructType, StructField, IntegerType, DateType, DecimalType, StringType

# Define schema
schema = StructType([
    StructField("order_id", IntegerType(), True),
    StructField("customer_id", IntegerType(), True),
    StructField("order_date", DateType(), True),
    StructField("total_amount", DecimalType(10, 2), True),
    StructField("status", StringType(), True)
])

# Create sample data
data = [
    (1, 101, "2024-01-15", 150.00, "completed"),
    (2, 102, "2024-01-16", 200.00, "pending"),
    (3, 101, "2024-01-17", 75.50, "completed"),
]

# Create DataFrame
df = spark.createDataFrame(data, schema)

# Write to managed table
df.write.mode("overwrite").option("mergeSchema", "true") \
    .format("delta") \
    .saveAsTable("sales_catalog.transactions.orders")

# Read the table
spark.sql("SELECT * FROM sales_catalog.transactions.orders").show()
```

### Topic 2: Basic Permission Management

#### SQL Examples:
```sql
-- Grant catalog-level permissions
GRANT USAGE ON CATALOG sales_catalog TO `analyst@company.com`;
GRANT CREATE ON CATALOG sales_catalog TO `data_engineer@company.com`;

-- Grant schema-level permissions
GRANT USAGE ON SCHEMA sales_catalog.transactions TO `analyst@company.com`;
GRANT SELECT ON SCHEMA sales_catalog.transactions TO `analyst@company.com`;

-- Grant table-level permissions
GRANT SELECT ON TABLE sales_catalog.transactions.orders 
    TO `analyst@company.com`;

-- Create group and grant permissions
CREATE GROUP IF NOT EXISTS analysts;
GRANT SELECT ON TABLE sales_catalog.transactions.orders TO `analysts`;

-- View current permissions
SHOW GRANTS ON TABLE sales_catalog.transactions.orders;
SHOW GRANTS TO `analyst@company.com`;
```

#### Python Example:
```python
# Check permissions programmatically
permissions = spark.sql("""
    SHOW GRANTS ON TABLE sales_catalog.transactions.orders
""").collect()

for perm in permissions:
    print(f"Principal: {perm[0]}, Permission: {perm[1]}")
```

### Topic 3: Understanding Managed vs External Tables

#### SQL Example:
```sql
-- Create a managed table (Unity Catalog manages storage)
CREATE TABLE sales_catalog.transactions.orders_managed (
    order_id INT,
    customer_id INT,
    amount DECIMAL(10, 2)
)
USING DELTA;

-- Create an external table (you manage storage)
CREATE TABLE sales_catalog.transactions.orders_external
LOCATION 's3://my-bucket/orders/'
USING DELTA;

-- Create foreign table (reference external metastore)
CREATE FOREIGN CATALOG external_catalog
USING ICEBERG
LOCATION 's3://my-bucket/iceberg/';

-- Query all tables
SELECT 
    table_catalog,
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'transactions';
```

### Topic 4: Basic Lineage and Auditing

#### SQL Example:
```sql
-- View table lineage
SELECT *
FROM system.access.audit
WHERE object_type = 'TABLE'
    AND object_name = 'orders'
    AND action = 'READ'
LIMIT 10;

-- View who accessed what and when
SELECT 
    timestamp,
    user_identity.email as user_email,
    action,
    object_name,
    response.status_code
FROM system.access.audit
WHERE date(timestamp) = current_date()
ORDER BY timestamp DESC;

-- Get lineage for a specific table
SELECT 
    input_tables,
    output_table,
    operation_type
FROM system.lineage.table_lineage
WHERE output_table LIKE '%orders%';
```

---

## Intermediate Level Topics

### Topic 1: Catalog Organization Strategies

#### Example: Environment-Based Organization
```sql
-- Create environment-specific catalogs
CREATE CATALOG IF NOT EXISTS sales_dev;
CREATE CATALOG IF NOT EXISTS sales_staging;
CREATE CATALOG IF NOT EXISTS sales_prod;

-- Create consistent schema structure across environments
CREATE SCHEMA IF NOT EXISTS sales_dev.raw;
CREATE SCHEMA IF NOT EXISTS sales_dev.curated;
CREATE SCHEMA IF NOT EXISTS sales_dev.analytics;

CREATE SCHEMA IF NOT EXISTS sales_staging.raw;
CREATE SCHEMA IF NOT EXISTS sales_staging.curated;
CREATE SCHEMA IF NOT EXISTS sales_staging.analytics;

CREATE SCHEMA IF NOT EXISTS sales_prod.raw;
CREATE SCHEMA IF NOT EXISTS sales_prod.curated;
CREATE SCHEMA IF NOT EXISTS sales_prod.analytics;

-- Example: Create medallion architecture tables
CREATE TABLE IF NOT EXISTS sales_prod.raw.orders_bronze (
    _metadata_extracted_at TIMESTAMP,
    _metadata_source_file STRING,
    order_data STRING  -- Raw JSON
)
USING DELTA;

CREATE TABLE IF NOT EXISTS sales_prod.curated.orders_silver (
    order_id INT,
    customer_id INT,
    order_date DATE,
    total_amount DECIMAL(10, 2),
    _processed_at TIMESTAMP,
    _updated_at TIMESTAMP
)
USING DELTA;

CREATE TABLE IF NOT EXISTS sales_prod.analytics.orders_gold (
    order_id INT,
    customer_id INT,
    order_date DATE,
    total_amount DECIMAL(10, 2),
    order_month DATE,
    order_year INT,
    customer_segment STRING
)
USING DELTA;
```

#### Python Example - Automation:
```python
def create_environment_catalogs(environments=['dev', 'staging', 'prod']):
    """Create catalog structure for multiple environments"""
    
    for env in environments:
        catalog_name = f"sales_{env}"
        
        # Create catalog
        spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog_name}")
        
        # Create standard schemas
        schemas = ['raw', 'curated', 'analytics']
        for schema in schemas:
            spark.sql(f"""
                CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema}
            """)
        
        print(f"✓ Created {catalog_name} with {len(schemas)} schemas")

# Execute
create_environment_catalogs()
```

### Topic 2: Storage Credentials and External Locations

#### SQL Example:
```sql
-- Create storage credential (for cloud storage access)
CREATE STORAGE CREDENTIAL IF NOT EXISTS my_s3_credential
  PROVIDER = 'AWS'
  COMMENT = 'S3 credential for external data access'
  AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/databricks-unity-catalog-role';

-- Create external location
CREATE EXTERNAL LOCATION IF NOT EXISTS my_data_location
  URL = 's3://my-data-bucket/external-tables/'
  WITH (CREDENTIAL = my_s3_credential)
  COMMENT = 'External location for raw data files';

-- Create external table pointing to external location
CREATE TABLE sales_prod.raw.customer_data_external
LOCATION 's3://my-data-bucket/external-tables/customers/'
USING DELTA;

-- View storage credentials
SHOW STORAGE CREDENTIALS;
```

#### Python Example:
```python
# List all external locations
external_locations = spark.sql("""
    SELECT name, url, credential_name
    FROM system.information_schema.external_locations
""").collect()

for loc in external_locations:
    print(f"Location: {loc.name}, URL: {loc.url}")
```

### Topic 3: Dynamic Views for Security

<cite index="16-1">Dynamic views wrap one or more base tables in a SQL view that filters rows, masks columns, or reshapes data, typically gated by group-membership functions like is_account_group_member().</cite>

#### SQL Example: Column Masking
```sql
-- Base table with sensitive data
CREATE TABLE sales_prod.transactions.employee_data (
    employee_id INT,
    name STRING,
    email STRING,
    salary DECIMAL(10, 2),
    department STRING
);

-- Dynamic view that masks sensitive columns
CREATE VIEW sales_prod.transactions.employee_view AS
SELECT 
    employee_id,
    name,
    CASE 
        WHEN is_account_group_member('hr_team') THEN email
        ELSE CONCAT(SUBSTRING(email, 1, 2), '***@company.com') 
    END AS email,
    CASE 
        WHEN is_account_group_member('managers') THEN salary
        ELSE 0
    END AS salary,
    department
FROM sales_prod.transactions.employee_data;

-- Test the view
SELECT * FROM sales_prod.transactions.employee_view;
```

#### SQL Example: Row Filtering
```sql
-- Dynamic view filtering rows by department
CREATE VIEW sales_prod.transactions.employee_dept_view AS
SELECT 
    employee_id,
    name,
    email,
    salary,
    department
FROM sales_prod.transactions.employee_data
WHERE CASE 
    WHEN is_account_group_member('sales_team') THEN department = 'Sales'
    WHEN is_account_group_member('engineering_team') THEN department = 'Engineering'
    ELSE FALSE
END;

-- Verify the view
SELECT COUNT(*) as visible_rows 
FROM sales_prod.transactions.employee_dept_view;
```

### Topic 4: Data Classification and Tagging

#### SQL Example:
```sql
-- Create a governed tag
CREATE TAG IF NOT EXISTS data_classification;
CREATE TAG IF NOT EXISTS sensitivity_level;

-- Tag a column as sensitive
ALTER TABLE sales_prod.transactions.employee_data
ALTER COLUMN salary SET TAG sensitivity_level = 'confidential';

ALTER TABLE sales_prod.transactions.employee_data
ALTER COLUMN email SET TAG data_classification = 'pii';

-- Query tagged columns
SELECT 
    table_name,
    column_name,
    tag_name,
    tag_value
FROM information_schema.column_tags
WHERE table_name = 'employee_data';

-- Find all PII columns
SELECT DISTINCT
    table_catalog,
    table_schema,
    table_name,
    column_name
FROM information_schema.column_tags
WHERE tag_name = 'data_classification' 
  AND tag_value = 'pii';
```

---

## Advanced Level Topics

### Topic 1: Attribute-Based Access Control (ABAC) Policies

<cite index="13-1">An ABAC policy evaluates tag-based conditions and applies row filters, which control which rows a user sees, and column masks, which control what values a user sees for specific columns, automatically to every matching object across entire catalogs and schemas.</cite>

#### SQL Example:
```sql
-- Create governed tags for ABAC
CREATE TAG IF NOT EXISTS data_sensitivity;
CREATE TAG IF NOT EXISTS business_domain;
CREATE TAG IF NOT EXISTS data_owner;

-- Tag tables/columns
ALTER TABLE sales_prod.curated.customers 
    SET TAG data_sensitivity = 'confidential';

ALTER TABLE sales_prod.curated.customers 
    COLUMN email SET TAG data_sensitivity = 'pii';

-- Create masking function for PII data
CREATE OR REPLACE FUNCTION sales_prod.curated.mask_pii(value STRING)
RETURNS STRING
AS $$
    CASE 
        WHEN is_account_group_member('data_governance_team') 
            THEN value
        ELSE CONCAT(SUBSTRING(value, 1, 1), '***')
    END
$$;

-- Create row filter function
CREATE OR REPLACE FUNCTION sales_prod.curated.filter_by_region(
    customer_region STRING
)
RETURNS BOOLEAN
AS $$
    CASE 
        WHEN is_account_group_member('na_sales_team') THEN customer_region = 'NA'
        WHEN is_account_group_member('emea_sales_team') THEN customer_region = 'EMEA'
        WHEN is_account_group_member('apac_sales_team') THEN customer_region = 'APAC'
        ELSE FALSE
    END
$$;

-- Apply the masking function as ABAC policy
-- (Would be configured through UI or API in practice)
```

#### Python Example: Setting Up ABAC at Scale
```python
from pyspark.sql import SparkSession

def setup_abac_policies(catalog_name, schema_name):
    """Set up ABAC policies across multiple tables"""
    
    # Define policy rules
    policies = {
        'pii_mask': {
            'tag': 'data_classification:pii',
            'action': 'column_mask',
            'function': 'mask_pii'
        },
        'region_filter': {
            'tag': 'region_assignment',
            'action': 'row_filter',
            'function': 'filter_by_region'
        }
    }
    
    # Get all tables in schema
    tables = spark.sql(f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_catalog = '{catalog_name}' 
        AND table_schema = '{schema_name}'
    """).collect()
    
    print(f"Found {len(tables)} tables in {catalog_name}.{schema_name}")
    
    for table in tables:
        print(f"Processing: {table.table_name}")
        # Policy application logic would go here
    
    return True

# Execute
setup_abac_policies('sales_prod', 'curated')
```

### Topic 2: Row-Level Filtering and Column Masking

<cite index="11-1">Row filters restrict which rows a user can see in a table. The filter is a SQL user-defined function (UDF) that evaluates each row at query time.</cite>

#### SQL Example: Complete Implementation
```sql
-- Create the base table
CREATE TABLE IF NOT EXISTS sales_prod.transactions.sales_data (
    transaction_id INT,
    customer_id INT,
    employee_id INT,
    amount DECIMAL(10, 2),
    credit_card_last_4 STRING,
    region STRING,
    transaction_date DATE
)
USING DELTA;

-- Create row filter function
CREATE OR REPLACE FUNCTION sales_prod.transactions.row_filter_sales()
RETURNS BOOLEAN
LANGUAGE SQL
AS $$
  CASE 
    -- Managers see all regions
    WHEN is_account_group_member('managers') THEN TRUE
    -- Regional sales teams see their own region
    WHEN is_account_group_member('na_sales') AND region = 'North America' THEN TRUE
    WHEN is_account_group_member('eu_sales') AND region = 'Europe' THEN TRUE
    WHEN is_account_group_member('apac_sales') AND region = 'Asia Pacific' THEN TRUE
    ELSE FALSE
  END
$$;

-- Create column mask function for credit card
CREATE OR REPLACE FUNCTION sales_prod.transactions.mask_credit_card(
    card_last_4 STRING
)
RETURNS STRING
LANGUAGE SQL
AS $$
  CASE
    -- Finance team and managers see full data
    WHEN is_account_group_member('finance_team') 
         OR is_account_group_member('managers') THEN card_last_4
    -- Everyone else sees masked value
    ELSE 'XXXX'
  END
$$;

-- Apply row filter to table
ALTER TABLE sales_prod.transactions.sales_data
ADD ROW FILTER row_filter_sales() ON ();

-- Apply column mask to credit card column
ALTER TABLE sales_prod.transactions.sales_data
ADD COLUMN MASK mask_credit_card() ON COLUMN credit_card_last_4;

-- Verify policies are applied
SELECT * FROM information_schema.column_masks
WHERE table_name = 'sales_data';

-- Test: A regional sales user should only see their region
SELECT 
    region,
    COUNT(*) as visible_transactions
FROM sales_prod.transactions.sales_data
GROUP BY region;
```

### Topic 3: Advanced Lineage and Governance

#### SQL Example: Data Lineage Queries
```sql
-- View table-to-table lineage
SELECT 
    upstream_table,
    downstream_table,
    transformation_type
FROM system.lineage.table_lineage
WHERE upstream_table LIKE 'sales_prod.raw.%'
ORDER BY upstream_table;

-- Column-level lineage (shows which columns derive from which)
SELECT *
FROM system.lineage.column_lineage
WHERE output_column LIKE 'sales_prod.analytics.%'
LIMIT 10;

-- Find all tables that depend on a specific table
WITH RECURSIVE dependencies AS (
    SELECT 
        output_table as table_name,
        upstream_table as source_table,
        1 as depth
    FROM system.lineage.table_lineage
    WHERE upstream_table = 'sales_prod.curated.customers'
    
    UNION ALL
    
    SELECT 
        tl.output_table,
        d.source_table,
        d.depth + 1
    FROM system.lineage.table_lineage tl
    JOIN dependencies d ON tl.upstream_table = d.table_name
    WHERE d.depth < 5  -- Limit recursion depth
)
SELECT DISTINCT table_name, depth
FROM dependencies
ORDER BY depth, table_name;

-- Audit trail for sensitive tables
SELECT 
    timestamp,
    user_identity.email as user_email,
    action,
    principal_id,
    object_name,
    object_type,
    response.result as action_result
FROM system.access.audit
WHERE object_name IN ('employee_data', 'salary_information')
    AND date(timestamp) >= current_date() - 7
ORDER BY timestamp DESC;
```

#### Python Example: Governance Dashboard Data
```python
from pyspark.sql.functions import col, count, desc, date_format

def create_governance_report():
    """Generate governance and access report"""
    
    # 1. Most accessed tables
    print("=== Top 10 Most Accessed Tables ===")
    top_tables = spark.sql("""
        SELECT 
            object_name,
            COUNT(*) as access_count,
            COUNT(DISTINCT user_identity.email) as unique_users,
            MAX(timestamp) as last_accessed
        FROM system.access.audit
        WHERE object_type = 'TABLE'
            AND date(timestamp) >= current_date() - 30
        GROUP BY object_name
        ORDER BY access_count DESC
        LIMIT 10
    """).show()
    
    # 2. Access violations or denied requests
    print("\n=== Access Denied Events (Last 24hrs) ===")
    denied = spark.sql("""
        SELECT 
            timestamp,
            user_identity.email,
            action,
            object_name,
            response.status_code,
            response.error_message
        FROM system.access.audit
        WHERE response.status_code != 200
            AND timestamp >= current_timestamp() - INTERVAL 1 DAY
        ORDER BY timestamp DESC
    """).show(truncate=False)
    
    # 3. Data quality metrics
    print("\n=== Table Health Metrics ===")
    health = spark.sql("""
        SELECT 
            table_catalog,
            table_schema,
            table_name,
            datediff(current_date(), cast(tbl_created_time/1000 as date)) as age_days,
            row_count,
            size_in_bytes
        FROM system.information_schema.tables
        WHERE table_catalog LIKE 'sales_%'
        ORDER BY row_count DESC
    """).show()
    
    return True

# Execute
create_governance_report()
```

### Topic 4: Multi-Format Catalog with Iceberg

<cite index="9-1">After a Delta Lake write transaction is completed, Databricks asynchronously generates a separate, corresponding metadata layer in the Iceberg format. This metadata generation process uses the same compute that performed the Delta transaction.</cite>

#### SQL Example:
```sql
-- Create Iceberg table in Unity Catalog
CREATE TABLE sales_prod.raw.iceberg_orders (
    order_id INT,
    customer_id INT,
    order_date DATE,
    amount DECIMAL(10, 2)
)
USING ICEBERG;

-- Write data to Iceberg table
INSERT INTO sales_prod.raw.iceberg_orders
SELECT * FROM sales_prod.raw.orders_delta;

-- Query with time travel
SELECT * 
FROM sales_prod.raw.iceberg_orders
VERSION AS OF 0;  -- Query specific version

-- Rollback to previous version
ALTER TABLE sales_prod.raw.iceberg_orders
SET TBLPROPERTIES ('current-snapshot-id' = <snapshot-id>);

-- Enable Iceberg compatibility on Delta table
ALTER TABLE sales_prod.raw.orders_delta
SET TBLPROPERTIES (
    'delta.enableIcebergCompatibility' = 'true',
    'delta.columnMapping.mode' = 'name'
);

-- UniForm support - serve to both Delta and Iceberg clients
SELECT 
    table_name,
    table_format,
    is_managed
FROM system.information_schema.tables
WHERE table_properties LIKE '%Iceberg%';
```

### Topic 5: Advanced Security with Sensitive Data

#### Python Example: Automated PII Detection and Protection
```python
from pyspark.sql.types import StringType
from pyspark.sql.functions import col, when, regexp_replace

class PIIProtector:
    """Handles PII detection and protection in Unity Catalog"""
    
    def __init__(self, catalog_name):
        self.catalog = catalog_name
        self.pii_patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^\d{3}-\d{3}-\d{4}$',
            'ssn': r'^\d{3}-\d{2}-\d{4}$',
            'credit_card': r'^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$'
        }
    
    def scan_for_pii(self, schema_name, table_name):
        """Scan table for PII patterns"""
        
        table_path = f"{self.catalog}.{schema_name}.{table_name}"
        df = spark.table(table_path)
        
        findings = {}
        
        for col_name in df.columns:
            if df.select(col_name).dtypes[0][1] == 'string':
                for pii_type, pattern in self.pii_patterns.items():
                    # Simple pattern check
                    matches = df.filter(
                        col(col_name).rlike(pattern)
                    ).count()
                    
                    if matches > 0:
                        if pii_type not in findings:
                            findings[pii_type] = []
                        findings[pii_type].append({
                            'column': col_name,
                            'matches': matches
                        })
        
        return findings
    
    def apply_pii_protection(self, schema_name, table_name, 
                              pii_columns):
        """Apply masking to identified PII columns"""
        
        table_path = f"{self.catalog}.{schema_name}.{table_name}"
        
        # Create masking function
        for col_name in pii_columns:
            mask_func_name = f"mask_{col_name}"
            
            spark.sql(f"""
                CREATE OR REPLACE FUNCTION 
                {self.catalog}.{schema_name}.{mask_func_name}
                (value STRING)
                RETURNS STRING
                LANGUAGE SQL
                AS $$
                    CASE
                        WHEN is_account_group_member('data_protection_team')
                            THEN value
                        ELSE '***MASKED***'
                    END
                $$
            """)
            
            # Apply mask
            spark.sql(f"""
                ALTER TABLE {table_path}
                ALTER COLUMN {col_name}
                SET MASK {mask_func_name}()
            """)
        
        print(f"✓ Applied masking to {len(pii_columns)} columns")

# Usage
protector = PIIProtector('sales_prod')
findings = protector.scan_for_pii('curated', 'customers')
print(f"PII Found: {findings}")
protector.apply_pii_protection('curated', 'customers', 
                               ['email', 'phone', 'ssn'])
```

### Topic 6: Predictive Optimization and Data Quality

#### SQL Example: Data Quality Monitoring
```sql
-- Check table statistics and quality metrics
SELECT 
    table_catalog,
    table_schema,
    table_name,
    row_count,
    size_in_bytes,
    CASE 
        WHEN size_in_bytes = 0 THEN 'Empty'
        WHEN row_count = 0 THEN 'No Data'
        WHEN row_count IS NULL THEN 'Stale Stats'
        ELSE 'Healthy'
    END as data_health
FROM system.information_schema.tables
WHERE table_catalog = 'sales_prod'
ORDER BY row_count DESC;

-- Monitor table operation history for optimization
SELECT 
    table_name,
    operation,
    COUNT(*) as operation_count,
    AVG(duration_ms) as avg_duration_ms
FROM system.operation.history
WHERE table_name LIKE 'sales_prod.%'
    AND operation IN ('OPTIMIZE', 'VACUUM', 'WRITE')
GROUP BY table_name, operation
ORDER BY operation_count DESC;

-- Identify optimization candidates (large tables with fragmentation)
SELECT 
    t.table_name,
    t.row_count,
    t.size_in_bytes,
    COUNT(DISTINCT f.file_name) as file_count,
    ROUND(AVG(f.file_size_bytes) / 1024 / 1024, 2) as avg_file_size_mb
FROM system.information_schema.tables t
LEFT JOIN system.files f ON t.table_name = f.table_name
WHERE t.table_catalog = 'sales_prod'
GROUP BY t.table_name, t.row_count, t.size_in_bytes
HAVING COUNT(DISTINCT f.file_name) > 1000  -- Fragmented
ORDER BY file_count DESC;
```

#### Python Example: Predictive Optimization Setup
```python
def setup_predictive_optimization(catalog_name, schema_name):
    """Enable Predictive Optimization for tables"""
    
    # Get all tables
    tables = spark.sql(f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_catalog = '{catalog_name}'
            AND table_schema = '{schema_name}'
    """).collect()
    
    for table in tables:
        table_name = table.table_name
        full_path = f"{catalog_name}.{schema_name}.{table_name}"
        
        try:
            # Enable Predictive Optimization
            spark.sql(f"""
                ALTER TABLE {full_path}
                SET TBLPROPERTIES (
                    'delta.enableDeletionVectors' = 'true',
                    'delta.columnMapping.mode' = 'name'
                )
            """)
            
            # Run OPTIMIZE
            spark.sql(f"OPTIMIZE {full_path}")
            
            print(f"✓ Optimized: {full_path}")
        except Exception as e:
            print(f"✗ Failed {full_path}: {str(e)}")

setup_predictive_optimization('sales_prod', 'curated')
```

---

## Use Cases

### 1. Financial Services - PCI-DSS Compliance
```sql
-- Create compliance-ready structure
CREATE CATALOG IF NOT EXISTS financial_prod;

CREATE TABLE financial_prod.transactions.payment_records (
    transaction_id STRING,
    customer_id INT,
    card_last_4 STRING,
    amount DECIMAL(15, 2),
    merchant_name STRING,
    transaction_timestamp TIMESTAMP
);

-- Implement column-level masking for PCI compliance
ALTER TABLE financial_prod.transactions.payment_records
ALTER COLUMN card_last_4 
SET MASK mask_payment_card()
ON ();

-- Audit all access to payment data
SELECT * FROM system.access.audit
WHERE object_name = 'payment_records'
ORDER BY timestamp DESC;
```

### 2. Healthcare - HIPAA Compliance
```sql
-- Create HIPAA-compliant structure
CREATE CATALOG IF NOT EXISTS healthcare_prod;

-- Create patient data table with built-in privacy controls
CREATE TABLE healthcare_prod.clinical.patient_records (
    patient_id STRING,
    patient_name STRING,
    date_of_birth DATE,
    medical_record STRING,
    diagnosis STRING,
    treatment_plan STRING
);

-- Implement fine-grained access control
CREATE OR REPLACE FUNCTION healthcare_prod.clinical.hipaa_filter()
RETURNS BOOLEAN
LANGUAGE SQL
AS $$
  CASE 
    WHEN is_account_group_member('treating_physicians') THEN TRUE
    WHEN is_account_group_member('clinical_researchers') 
         AND treatment_plan IS NOT NULL THEN TRUE
    ELSE FALSE
  END
$$;

ALTER TABLE healthcare_prod.clinical.patient_records
ADD ROW FILTER hipaa_filter() ON ();
```

### 3. E-commerce - Customer Data Platform
```sql
-- Create CDP structure
CREATE CATALOG IF NOT EXISTS ecommerce_prod;
CREATE SCHEMA ecommerce_prod.customer_data;
CREATE SCHEMA ecommerce_prod.analytics;

-- Bronze layer - raw events
CREATE TABLE ecommerce_prod.customer_data.events_bronze (
    event_id STRING,
    customer_id STRING,
    event_type STRING,
    event_properties STRING,
    event_timestamp TIMESTAMP
)
USING DELTA
PARTITIONED BY (year INT, month INT);

-- Silver layer - cleaned customer profiles
CREATE TABLE ecommerce_prod.customer_data.customer_profiles_silver (
    customer_id STRING,
    email STRING,
    phone STRING,
    lifetime_value DECIMAL(10, 2),
    segment STRING,
    last_purchase_date DATE,
    updated_at TIMESTAMP
)
USING DELTA;

-- Gold layer - analytics-ready
CREATE TABLE ecommerce_prod.analytics.customer_metrics_gold (
    customer_id STRING,
    total_purchases INT,
    avg_order_value DECIMAL(10, 2),
    churn_risk_score DECIMAL(3, 2),
    segment STRING,
    cohort STRING
)
USING DELTA;

-- Tag sensitive columns
ALTER TABLE ecommerce_prod.customer_data.customer_profiles_silver
ALTER COLUMN email SET TAG data_classification = 'pii';

ALTER TABLE ecommerce_prod.customer_data.customer_profiles_silver
ALTER COLUMN phone SET TAG data_classification = 'pii';
```

---

## Best Practices

### 1. Organizational Structure
- Use 3-10 catalogs per metastore
- Use environment-based catalogs (dev, staging, prod) as default
- Create schemas by medallion layer (raw, curated, analytics) or domain
- Document catalog and schema purposes
- Use consistent naming conventions

### 2. Access Control
- Implement principle of least privilege
- Use account-level groups for consistency
- Leverage ABAC policies for scalability
- Tag data consistently for automated policy application
- Regularly audit access patterns

### 3. Data Quality
- Enable deletion vectors for better performance
- Use OPTIMIZE regularly for large tables
- Monitor table statistics and health
- Implement data quality checks in lineage
- Use Predictive Optimization for large workloads

### 4. Security
- Never store production data on DBFS
- Use managed credentials for external access
- Implement column masking for PII data
- Use row filtering for department/region separation
- Enable audit logging for sensitive tables

### 5. Performance
- Partition large tables appropriately
- Use Iceberg for multi-format workloads
- Enable liquid clustering where appropriate
- Monitor query performance against filtered tables
- Use serverless compute for dynamic views

### 6. Governance
- Track data lineage at column level
- Document data ownership per schema
- Review permissions quarterly
- Maintain runbooks for recovery procedures
- Use system tables for compliance reporting

---

## Summary

Databricks Unity Catalog provides a comprehensive, enterprise-grade governance solution that unifies access control, data quality, lineage tracking, and compliance across the entire data platform. From basic permission management to advanced ABAC policies and multi-format support, it scales from small teams to large enterprises while maintaining security and performance.

### Key Takeaways:
1. **Three-level namespace**: Metastore → Catalog → Schema → Object
2. **Multiple access methods**: Standard (multi-user) and Dedicated (single-user) modes
3. **Fine-grained controls**: Row-level filtering, column masking, and ABAC policies
4. **Enterprise features**: Lineage tracking, audit logging, data quality monitoring
5. **Open ecosystem**: Supports Delta, Iceberg, and OpenSharing
6. **Automated governance**: Classification, tagging, and policy application at scale
