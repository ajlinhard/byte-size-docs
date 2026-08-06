-- ============================================================================
-- DATABRICKS UNITY CATALOG - ADVANCED SQL PATTERNS AND BEST PRACTICES
-- ============================================================================

-- This file contains production-ready SQL patterns for various UC scenarios


-- ============================================================================
-- SECTION 1: CATALOG AND SCHEMA SETUP PATTERNS
-- ============================================================================

-- Pattern 1: Environment-Based Structure
-- Best for: Organizations with dev/staging/prod environments

CREATE CATALOG IF NOT EXISTS ecommerce_dev;
CREATE CATALOG IF NOT EXISTS ecommerce_staging;
CREATE CATALOG IF NOT EXISTS ecommerce_prod;

-- Create consistent schema structure across environments
CREATE SCHEMA IF NOT EXISTS ecommerce_prod.raw_data 
COMMENT 'Raw data ingestion layer';

CREATE SCHEMA IF NOT EXISTS ecommerce_prod.refined_data 
COMMENT 'Cleaned and standardized data';

CREATE SCHEMA IF NOT EXISTS ecommerce_prod.analytics_layer 
COMMENT 'Analytics-ready aggregated tables';

CREATE SCHEMA IF NOT EXISTS ecommerce_prod.ml_features 
COMMENT 'ML features and training datasets';


-- Pattern 2: Domain-Based Structure
-- Best for: Data mesh and federated governance models

CREATE CATALOG IF NOT EXISTS customer_domain;
CREATE CATALOG IF NOT EXISTS product_domain;
CREATE CATALOG IF NOT EXISTS finance_domain;
CREATE CATALOG IF NOT EXISTS operations_domain;

CREATE SCHEMA IF NOT EXISTS customer_domain.public;
CREATE SCHEMA IF NOT EXISTS customer_domain.internal;
CREATE SCHEMA IF NOT EXISTS customer_domain.sandbox;


-- Pattern 3: Hybrid Structure (Environment + Domain)
-- Best for: Large enterprises with multiple business units

CREATE CATALOG IF NOT EXISTS sales_prod;
CREATE SCHEMA IF NOT EXISTS sales_prod.raw;
CREATE SCHEMA IF NOT EXISTS sales_prod.curated;
CREATE SCHEMA IF NOT EXISTS sales_prod.analytics;

CREATE CATALOG IF NOT EXISTS marketing_prod;
CREATE SCHEMA IF NOT EXISTS marketing_prod.raw;
CREATE SCHEMA IF NOT EXISTS marketing_prod.curated;
CREATE SCHEMA IF NOT EXISTS marketing_prod.analytics;


-- ============================================================================
-- SECTION 2: TABLE CREATION PATTERNS
-- ============================================================================

-- Pattern 1: Bronze Layer - Raw Ingestion
CREATE TABLE IF NOT EXISTS sales_prod.raw.orders_bronze (
    -- Surrogate key
    _record_id STRING NOT NULL,
    -- Source metadata
    _source_system STRING NOT NULL,
    _source_file STRING,
    _extraction_date DATE,
    _extraction_timestamp TIMESTAMP,
    _extraction_batch_id STRING,
    -- Raw data (often stored as JSON for flexibility)
    raw_data STRING NOT NULL,
    -- Standard metadata
    _ingested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    _ingestion_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    -- Data quality flags
    _is_valid BOOLEAN DEFAULT TRUE,
    _parsing_error STRING
)
USING DELTA
PARTITIONED BY (_extraction_date)
COMMENT 'Raw order data from source systems';

-- Enable optimized storage
ALTER TABLE sales_prod.raw.orders_bronze 
SET TBLPROPERTIES (
    'delta.enableDeletionVectors' = 'true',
    'delta.columnMapping.mode' = 'name',
    'delta.optimize.write.enabled' = 'true'
);


-- Pattern 2: Silver Layer - Cleaned and Standardized
CREATE TABLE IF NOT EXISTS sales_prod.curated.orders_silver (
    -- Surrogate keys
    order_id STRING NOT NULL,
    customer_id STRING NOT NULL,
    -- Business dimensions
    order_date DATE NOT NULL,
    order_month DATE NOT NULL,
    order_year INT NOT NULL,
    region STRING NOT NULL,
    -- Measures
    order_amount DECIMAL(15, 2) NOT NULL,
    discount_amount DECIMAL(15, 2) DEFAULT 0,
    net_amount DECIMAL(15, 2) NOT NULL,
    tax_amount DECIMAL(15, 2) NOT NULL,
    total_amount DECIMAL(15, 2) NOT NULL,
    -- Dimensions
    order_status STRING NOT NULL,
    payment_method STRING,
    fulfillment_status STRING,
    -- Metadata
    _processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    _updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    _dq_checks_passed BOOLEAN DEFAULT TRUE,
    _dq_error_message STRING,
    -- Lineage
    _bronze_record_id STRING
)
USING DELTA
PARTITIONED BY (order_year, order_month)
CLUSTERED BY (customer_id) INTO 10 BUCKETS
COMMENT 'Cleaned and validated order data';

CREATE INDEX idx_customer_date ON sales_prod.curated.orders_silver (customer_id, order_date);
CREATE INDEX idx_region_status ON sales_prod.curated.orders_silver (region, order_status);


-- Pattern 3: Gold Layer - Analytics Ready
CREATE TABLE IF NOT EXISTS sales_prod.analytics.orders_summary_gold (
    order_id STRING NOT NULL,
    customer_id STRING NOT NULL,
    order_date DATE NOT NULL,
    order_month DATE NOT NULL,
    order_year INT NOT NULL,
    region STRING NOT NULL,
    -- Aggregated measures
    total_amount DECIMAL(15, 2) NOT NULL,
    net_amount DECIMAL(15, 2) NOT NULL,
    line_items_count INT NOT NULL,
    unique_products INT NOT NULL,
    -- Customer context
    customer_segment STRING,
    customer_lifetime_value DECIMAL(15, 2),
    -- Derived metrics
    order_complexity_score DECIMAL(3, 2),
    fulfillment_days INT,
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
USING DELTA
PARTITIONED BY (order_year, order_month)
COMMENT 'Analytics-ready order summary';


-- ============================================================================
-- SECTION 3: DATA CLASSIFICATION AND TAGGING PATTERNS
-- ============================================================================

-- Pattern 1: Create Governed Tags
CREATE TAG IF NOT EXISTS data_sensitivity;
CREATE TAG IF NOT EXISTS pii_type;
CREATE TAG IF NOT EXISTS business_domain;
CREATE TAG IF NOT EXISTS data_owner;
CREATE TAG IF NOT EXISTS retention_period;
CREATE TAG IF NOT EXISTS compliance_requirement;

-- Pattern 2: Tag Tables with Metadata
ALTER TABLE sales_prod.curated.orders_silver SET TAG 
    data_sensitivity = 'high',
    business_domain = 'sales',
    data_owner = 'sales_analytics_team',
    compliance_requirement = 'sarbanes_oxley';

-- Pattern 3: Tag Individual Columns
ALTER TABLE sales_prod.curated.orders_silver 
ALTER COLUMN customer_id SET TAG pii_type = 'customer_identifier';

ALTER TABLE sales_prod.curated.orders_silver 
ALTER COLUMN order_amount SET TAG data_sensitivity = 'medium';

-- Query all tags
SELECT 
    table_name,
    column_name,
    tag_name,
    tag_value
FROM information_schema.column_tags
WHERE table_schema = 'curated'
ORDER BY table_name, column_name, tag_name;


-- ============================================================================
-- SECTION 4: SECURITY PATTERNS - ROW AND COLUMN LEVEL
-- ============================================================================

-- Pattern 1: Column Masking for PII
-- Create mask functions
CREATE OR REPLACE FUNCTION sales_prod.curated.mask_email(email_value STRING)
RETURNS STRING
LANGUAGE SQL
AS $$
    CASE 
        -- Data protection team sees full email
        WHEN is_account_group_member('data_protection_team') THEN email_value
        -- Internal analysts see masked version
        WHEN is_account_group_member('internal_users') THEN 
            CONCAT(SUBSTRING(email_value, 1, 2), '***@', SUBSTRING(email_value, INSTR(email_value, '@') + 1))
        -- External users see fully masked
        ELSE '***@***'
    END
$$;

CREATE OR REPLACE FUNCTION sales_prod.curated.mask_ssn(ssn_value STRING)
RETURNS STRING
LANGUAGE SQL
AS $$
    CASE 
        WHEN is_account_group_member('hr_team') THEN ssn_value
        WHEN is_account_group_member('managers') THEN CONCAT(SUBSTRING(ssn_value, 1, 5), '-XXXX')
        ELSE 'XXX-XX-XXXX'
    END
$$;

CREATE OR REPLACE FUNCTION sales_prod.curated.mask_salary(salary_value DECIMAL(10, 2))
RETURNS DECIMAL(10, 2)
LANGUAGE SQL
AS $$
    CASE
        WHEN is_account_group_member('finance_team') THEN salary_value
        WHEN is_account_group_member('managers') THEN ROUND(salary_value, -3)  -- Round to nearest thousand
        ELSE NULL
    END
$$;

-- Apply column masks
ALTER TABLE sales_prod.curated.orders_silver 
ALTER COLUMN customer_email SET MASK mask_email();

-- Note: Apply masks only on columns with PII data


-- Pattern 2: Row Level Filtering
CREATE OR REPLACE FUNCTION sales_prod.curated.filter_by_region()
RETURNS BOOLEAN
LANGUAGE SQL
AS $$
    CASE 
        -- Managers can see all regions
        WHEN is_account_group_member('sales_managers') THEN TRUE
        -- North America team sees only NA region
        WHEN is_account_group_member('na_sales_team') AND region = 'North America' THEN TRUE
        -- Europe team sees only Europe region
        WHEN is_account_group_member('eu_sales_team') AND region = 'Europe' THEN TRUE
        -- APAC team sees only Asia-Pacific region
        WHEN is_account_group_member('apac_sales_team') AND region = 'Asia-Pacific' THEN TRUE
        -- Deny by default
        ELSE FALSE
    END
$$;

-- Apply row filter
ALTER TABLE sales_prod.curated.orders_silver
ADD ROW FILTER filter_by_region() ON ();


-- Pattern 3: Dynamic Views with Security
-- Create view that enforces column and row level security without modifying base table
CREATE OR REPLACE VIEW sales_prod.curated.orders_secure_view AS
SELECT 
    order_id,
    customer_id,
    -- Conditionally show customer email
    CASE 
        WHEN is_account_group_member('customer_service') THEN customer_email
        ELSE 'REDACTED'
    END AS customer_email,
    order_date,
    order_month,
    region,
    -- Conditionally show sensitive amounts
    CASE 
        WHEN is_account_group_member('finance_team') THEN order_amount
        ELSE 0
    END AS order_amount,
    CASE 
        WHEN is_account_group_member('finance_team') THEN net_amount
        ELSE 0
    END AS net_amount,
    order_status,
    _processed_at
FROM sales_prod.curated.orders_silver
WHERE 
    -- Row filtering by region
    CASE 
        WHEN is_account_group_member('sales_managers') THEN TRUE
        WHEN is_account_group_member('na_sales_team') AND region = 'North America' THEN TRUE
        WHEN is_account_group_member('eu_sales_team') AND region = 'Europe' THEN TRUE
        ELSE FALSE
    END;

-- Verify view is working
SELECT * FROM sales_prod.curated.orders_secure_view LIMIT 5;


-- ============================================================================
-- SECTION 5: PERMISSION MANAGEMENT PATTERNS
-- ============================================================================

-- Pattern 1: Create Groups with Layered Access
CREATE GROUP IF NOT EXISTS sales_analysts;
CREATE GROUP IF NOT EXISTS data_engineers;
CREATE GROUP IF NOT EXISTS finance_team;
CREATE GROUP IF NOT EXISTS executives;
CREATE GROUP IF NOT EXISTS data_governance;

-- Pattern 2: Grant Catalog-Level Permissions
-- Sales team: can use sales catalog, create schemas, but no drop
GRANT USAGE ON CATALOG sales_prod TO `sales_analysts`;
GRANT CREATE ON CATALOG sales_prod TO `sales_analysts`;

-- Data engineers: full control over data creation
GRANT USAGE ON CATALOG sales_prod TO `data_engineers`;
GRANT CREATE ON CATALOG sales_prod TO `data_engineers`;

-- Finance: read-only access to analytics
GRANT USAGE ON CATALOG sales_prod TO `finance_team`;

-- Executives: read-only on aggregated data
GRANT USAGE ON CATALOG sales_prod TO `executives`;


-- Pattern 3: Grant Schema-Level Permissions
-- Analytics team gets SELECT on curated and analytics layers
GRANT USAGE ON SCHEMA sales_prod.curated TO `sales_analysts`;
GRANT SELECT ON SCHEMA sales_prod.curated TO `sales_analysts`;

GRANT USAGE ON SCHEMA sales_prod.analytics_layer TO `sales_analysts`;
GRANT SELECT ON SCHEMA sales_prod.analytics_layer TO `sales_analysts`;

-- Data engineers: modify curated data
GRANT USAGE ON SCHEMA sales_prod.curated TO `data_engineers`;
GRANT SELECT, MODIFY ON SCHEMA sales_prod.curated TO `data_engineers`;

-- Finance: read financial tables
GRANT USAGE ON SCHEMA sales_prod.analytics_layer TO `finance_team`;
GRANT SELECT ON TABLE sales_prod.analytics_layer.financial_summary TO `finance_team`;


-- Pattern 4: Grant Table-Level Permissions
-- Everyone can read orders summary
GRANT SELECT ON TABLE sales_prod.analytics_layer.orders_summary_gold 
TO `sales_analysts`;

GRANT SELECT ON TABLE sales_prod.analytics_layer.orders_summary_gold 
TO `finance_team`;

GRANT SELECT ON TABLE sales_prod.analytics_layer.orders_summary_gold 
TO `executives`;

-- Only data engineers can modify silver layer
GRANT SELECT, MODIFY ON TABLE sales_prod.curated.orders_silver 
TO `data_engineers`;


-- Pattern 5: Revoke Permissions
REVOKE SELECT ON TABLE sales_prod.raw.orders_bronze FROM `sales_analysts`;
REVOKE CREATE ON SCHEMA sales_prod.raw FROM `sales_analysts`;


-- Pattern 6: View Current Permissions
-- Check group membership
SELECT 
    principal_id,
    principal_type,
    privileges
FROM system.access.principals
WHERE group_name = 'sales_analysts';

-- Check table permissions
SELECT * FROM INFORMATION_SCHEMA.ROLE_PRIVILEGES 
WHERE table_name = 'orders_silver';

-- Get all grants on a table
SHOW GRANTS ON TABLE sales_prod.curated.orders_silver;


-- ============================================================================
-- SECTION 6: DATA QUALITY AND VALIDATION PATTERNS
-- ============================================================================

-- Pattern 1: Data Quality Check View
CREATE OR REPLACE VIEW sales_prod.curated.dq_orders_health AS
SELECT 
    'order_completeness' as check_name,
    COUNT(*) as total_records,
    COUNT(order_id) as non_null_order_ids,
    ROUND(100.0 * COUNT(order_id) / COUNT(*), 2) as completeness_pct,
    COUNT(CASE WHEN order_amount > 0 THEN 1 END) as valid_amounts,
    CURRENT_TIMESTAMP() as check_timestamp
FROM sales_prod.curated.orders_silver
UNION ALL
SELECT 
    'order_amount_validity',
    COUNT(*),
    COUNT(CASE WHEN total_amount >= net_amount THEN 1 END),
    ROUND(100.0 * COUNT(CASE WHEN total_amount >= net_amount THEN 1 END) / COUNT(*), 2),
    COUNT(CASE WHEN order_amount > 0 THEN 1 END),
    CURRENT_TIMESTAMP()
FROM sales_prod.curated.orders_silver
UNION ALL
SELECT 
    'order_date_validity',
    COUNT(*),
    COUNT(CASE WHEN order_date <= CURRENT_DATE() THEN 1 END),
    ROUND(100.0 * COUNT(CASE WHEN order_date <= CURRENT_DATE() THEN 1 END) / COUNT(*), 2),
    COUNT(CASE WHEN order_date >= DATE_SUB(CURRENT_DATE(), 3650) THEN 1 END),
    CURRENT_TIMESTAMP()
FROM sales_prod.curated.orders_silver;

-- Query quality metrics
SELECT * FROM sales_prod.curated.dq_orders_health;


-- Pattern 2: Anomaly Detection
CREATE OR REPLACE VIEW sales_prod.curated.dq_anomalies AS
WITH daily_stats AS (
    SELECT 
        order_date,
        COUNT(*) as daily_orders,
        AVG(order_amount) as avg_amount,
        MAX(order_amount) as max_amount,
        STDDEV(order_amount) as stddev_amount
    FROM sales_prod.curated.orders_silver
    GROUP BY order_date
),
stats_with_baseline AS (
    SELECT 
        order_date,
        daily_orders,
        avg_amount,
        max_amount,
        stddev_amount,
        AVG(daily_orders) OVER (ORDER BY order_date ROWS BETWEEN 30 PRECEDING AND CURRENT ROW) as rolling_avg_orders,
        AVG(avg_amount) OVER (ORDER BY order_date ROWS BETWEEN 30 PRECEDING AND CURRENT ROW) as rolling_avg_amount
    FROM daily_stats
)
SELECT 
    order_date,
    daily_orders,
    rolling_avg_orders,
    ROUND(100.0 * (daily_orders - rolling_avg_orders) / rolling_avg_orders, 2) as pct_change,
    CASE 
        WHEN ABS(daily_orders - rolling_avg_orders) > 2 * stddev_amount THEN 'ANOMALY'
        ELSE 'NORMAL'
    END as anomaly_flag,
    avg_amount,
    rolling_avg_amount
FROM stats_with_baseline
WHERE order_date >= CURRENT_DATE() - 90;


-- ============================================================================
-- SECTION 7: LINEAGE AND AUDIT PATTERNS
-- ============================================================================

-- Pattern 1: Table Lineage Query
SELECT 
    upstream_table,
    downstream_table,
    COUNT(*) as transformation_count
FROM system.lineage.table_lineage
WHERE upstream_table LIKE 'sales_prod.raw.%'
    OR downstream_table LIKE 'sales_prod.%'
GROUP BY upstream_table, downstream_table
ORDER BY upstream_table;


-- Pattern 2: Column Lineage
SELECT 
    upstream_table,
    upstream_column,
    downstream_table,
    output_column,
    transformation
FROM system.lineage.column_lineage
WHERE downstream_table LIKE 'sales_prod.analytics.%'
ORDER BY downstream_table, output_column;


-- Pattern 3: Access Audit Trail
SELECT 
    DATE(timestamp) as access_date,
    HOUR(timestamp) as hour,
    user_identity.email as user_email,
    action,
    object_name,
    response.status_code as status,
    COUNT(*) as access_count
FROM system.access.audit
WHERE 
    object_type = 'TABLE' 
    AND object_name LIKE 'orders_%'
    AND timestamp >= CURRENT_DATE() - 30
GROUP BY DATE(timestamp), HOUR(timestamp), user_email, action, object_name, status
ORDER BY access_date DESC, hour DESC, access_count DESC;


-- Pattern 4: Security Events
SELECT 
    timestamp,
    user_identity.email,
    action,
    object_name,
    response.status_code,
    response.error_message
FROM system.access.audit
WHERE response.status_code >= 400
    AND timestamp >= CURRENT_TIMESTAMP() - INTERVAL 24 HOUR
ORDER BY timestamp DESC;


-- ============================================================================
-- SECTION 8: PERFORMANCE AND OPTIMIZATION PATTERNS
-- ============================================================================

-- Pattern 1: Table Statistics and Optimization
-- Analyze table
ANALYZE TABLE sales_prod.curated.orders_silver COMPUTE STATISTICS;

-- Optimize table (compact small files)
OPTIMIZE sales_prod.curated.orders_silver
WHERE order_year = YEAR(CURRENT_DATE());

-- With Z-order clustering
OPTIMIZE sales_prod.curated.orders_silver
WHERE order_year = YEAR(CURRENT_DATE())
ZORDER BY (customer_id, order_date);

-- Check optimization history
SELECT 
    table_name,
    operation,
    COUNT(*) as operation_count,
    MAX(timestamp) as last_operation,
    AVG(duration_ms) as avg_duration_ms
FROM system.operation.history
WHERE table_name LIKE 'sales_prod.%'
    AND operation IN ('OPTIMIZE', 'VACUUM')
GROUP BY table_name, operation
ORDER BY table_name;


-- Pattern 2: Vacuum Old Data
-- Remove files older than 7 days
VACUUM sales_prod.curated.orders_silver RETAIN 7 DAYS;


-- Pattern 3: Partition Pruning
-- This query will efficiently use partitions
SELECT 
    customer_id,
    SUM(order_amount) as total_spent
FROM sales_prod.curated.orders_silver
WHERE order_year = 2024 
    AND order_month >= '2024-01-01'
    AND order_month < '2024-04-01'
    AND region = 'North America'
GROUP BY customer_id
ORDER BY total_spent DESC;


-- Pattern 4: Identify Optimization Candidates
SELECT 
    t.table_catalog,
    t.table_schema,
    t.table_name,
    t.row_count,
    ROUND(t.size_in_bytes / 1024 / 1024 / 1024, 2) as size_gb,
    CASE 
        WHEN t.size_in_bytes > 10737418240 THEN 'LARGE'  -- > 10GB
        WHEN t.size_in_bytes > 1073741824 THEN 'MEDIUM'  -- > 1GB
        ELSE 'SMALL'
    END as size_category
FROM system.information_schema.tables t
WHERE t.table_catalog = 'sales_prod'
    AND t.table_schema IN ('curated', 'analytics_layer')
ORDER BY t.size_in_bytes DESC;


-- ============================================================================
-- SECTION 9: MEDALLION ARCHITECTURE ETL PATTERNS
-- ============================================================================

-- Pattern 1: Bronze to Silver Transformation
CREATE OR REPLACE VIEW sales_prod.curated.orders_silver_view AS
SELECT 
    -- Generate surrogate key
    MD5(CONCAT(get_json_object(raw_data, '$.order_id'), 
               get_json_object(raw_data, '$.order_date'))) as order_id,
    -- Parse JSON fields
    CAST(get_json_object(raw_data, '$.customer_id') AS STRING) as customer_id,
    CAST(get_json_object(raw_data, '$.order_date') AS DATE) as order_date,
    CAST(MONTH(CAST(get_json_object(raw_data, '$.order_date') AS DATE)) AS INT) as order_month,
    CAST(YEAR(CAST(get_json_object(raw_data, '$.order_date') AS DATE)) AS INT) as order_year,
    get_json_object(raw_data, '$.region') as region,
    CAST(get_json_object(raw_data, '$.order_amount') AS DECIMAL(15, 2)) as order_amount,
    CAST(get_json_object(raw_data, '$.discount') AS DECIMAL(15, 2)) as discount_amount,
    CAST(CAST(get_json_object(raw_data, '$.order_amount') AS DECIMAL(15, 2)) 
        - CAST(get_json_object(raw_data, '$.discount') AS DECIMAL(15, 2)) AS DECIMAL(15, 2)) as net_amount,
    CAST(get_json_object(raw_data, '$.tax') AS DECIMAL(15, 2)) as tax_amount,
    CAST(CAST(get_json_object(raw_data, '$.order_amount') AS DECIMAL(15, 2)) 
        + CAST(get_json_object(raw_data, '$.tax') AS DECIMAL(15, 2)) AS DECIMAL(15, 2)) as total_amount,
    get_json_object(raw_data, '$.order_status') as order_status,
    get_json_object(raw_data, '$.payment_method') as payment_method,
    CURRENT_TIMESTAMP() as _processed_at,
    _record_id as _bronze_record_id
FROM sales_prod.raw.orders_bronze
WHERE _is_valid = TRUE;


-- Pattern 2: Silver to Gold Aggregation
CREATE OR REPLACE TABLE sales_prod.analytics_layer.orders_daily_summary_gold AS
SELECT 
    order_date,
    region,
    COUNT(DISTINCT order_id) as order_count,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(net_amount) as total_revenue,
    AVG(order_amount) as avg_order_amount,
    MIN(order_amount) as min_order_amount,
    MAX(order_amount) as max_order_amount,
    STDDEV(order_amount) as stddev_order_amount,
    CURRENT_TIMESTAMP() as updated_at
FROM sales_prod.curated.orders_silver
GROUP BY order_date, region;

PARTITION BY (order_date);
CLUSTERED BY (region) INTO 8 BUCKETS;


-- ============================================================================
-- SECTION 10: COMPLIANCE AND GOVERNANCE PATTERNS
-- ============================================================================

-- Pattern 1: GDPR Right-to-be-Forgotten Implementation
-- Create a deletion tracking table
CREATE TABLE IF NOT EXISTS sales_prod.curated.deletion_requests (
    deletion_request_id STRING NOT NULL,
    customer_id STRING NOT NULL,
    deletion_type STRING,  -- 'FULL', 'PARTIAL'
    requested_date DATE,
    processed_date DATE,
    status STRING DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Mark records for deletion without physically deleting
CREATE OR REPLACE VIEW sales_prod.curated.orders_gdpr_compliant AS
SELECT 
    *
FROM sales_prod.curated.orders_silver
WHERE customer_id NOT IN (
    SELECT DISTINCT customer_id 
    FROM sales_prod.curated.deletion_requests
    WHERE status = 'APPROVED'
);


-- Pattern 2: Data Retention Policies
CREATE TABLE IF NOT EXISTS sales_prod.curated.retention_policy (
    table_name STRING,
    retention_days INT,
    policy_description STRING,
    created_date DATE,
    updated_date DATE
);

-- Query to identify expired data
SELECT 
    table_name,
    DATE_SUB(CURRENT_DATE(), retention_days) as cutoff_date,
    COUNT(*) as expired_records
FROM sales_prod.curated.orders_silver
JOIN sales_prod.curated.retention_policy rp
    ON orders_silver.table_name = rp.table_name
WHERE order_date < DATE_SUB(CURRENT_DATE(), rp.retention_days)
GROUP BY table_name, cutoff_date;


-- Pattern 3: Compliance Audit Report
SELECT 
    'Data Access' as audit_area,
    COUNT(DISTINCT user_identity.email) as unique_users,
    COUNT(*) as total_access_events,
    MIN(timestamp) as earliest_access,
    MAX(timestamp) as latest_access,
    CURRENT_DATE() as report_date
FROM system.access.audit
WHERE timestamp >= DATE_SUB(CURRENT_DATE(), 90)
UNION ALL
SELECT 
    'Data Modifications',
    COUNT(DISTINCT user_identity.email),
    COUNT(*),
    MIN(timestamp),
    MAX(timestamp),
    CURRENT_DATE()
FROM system.access.audit
WHERE action IN ('CREATE', 'DELETE', 'ALTER', 'UPDATE')
    AND timestamp >= DATE_SUB(CURRENT_DATE(), 90)
UNION ALL
SELECT 
    'Access Denials',
    COUNT(DISTINCT user_identity.email),
    COUNT(*),
    MIN(timestamp),
    MAX(timestamp),
    CURRENT_DATE()
FROM system.access.audit
WHERE response.status_code >= 400
    AND timestamp >= DATE_SUB(CURRENT_DATE(), 90);


-- ============================================================================
-- SECTION 11: MONITORING AND ALERTING PATTERNS
-- ============================================================================

-- Pattern 1: Table Freshness Monitoring
SELECT 
    'orders_silver' as table_name,
    MAX(_processed_at) as last_update,
    DATEDIFF(CURRENT_TIMESTAMP(), MAX(_processed_at())) as hours_since_update,
    COUNT(*) as record_count,
    CASE 
        WHEN DATEDIFF(CURRENT_TIMESTAMP(), MAX(_processed_at)) > 24 THEN 'STALE'
        WHEN DATEDIFF(CURRENT_TIMESTAMP(), MAX(_processed_at)) > 12 THEN 'AGING'
        ELSE 'FRESH'
    END as freshness_status
FROM sales_prod.curated.orders_silver
GROUP BY table_name
UNION ALL
SELECT 
    'orders_gold',
    MAX(updated_at),
    DATEDIFF(CURRENT_TIMESTAMP(), MAX(updated_at)),
    COUNT(*),
    CASE 
        WHEN DATEDIFF(CURRENT_TIMESTAMP(), MAX(updated_at)) > 24 THEN 'STALE'
        WHEN DATEDIFF(CURRENT_TIMESTAMP(), MAX(updated_at)) > 12 THEN 'AGING'
        ELSE 'FRESH'
    END
FROM sales_prod.analytics_layer.orders_daily_summary_gold
GROUP BY table_name;


-- Pattern 2: Volume Anomaly Detection
WITH daily_volumes AS (
    SELECT 
        order_date,
        COUNT(*) as daily_count,
        AVG(COUNT(*)) OVER (ORDER BY order_date ROWS BETWEEN 30 PRECEDING AND CURRENT ROW) as avg_30day
    FROM sales_prod.curated.orders_silver
    GROUP BY order_date
)
SELECT 
    order_date,
    daily_count,
    avg_30day,
    ROUND(100 * (daily_count - avg_30day) / avg_30day, 2) as pct_change,
    CASE 
        WHEN ABS(daily_count - avg_30day) > 2 * STDDEV(daily_count) OVER (ORDER BY order_date ROWS BETWEEN 30 PRECEDING AND CURRENT ROW)
            THEN 'ALERT'
        ELSE 'NORMAL'
    END as alert_status
FROM daily_volumes
WHERE order_date >= CURRENT_DATE() - 30
ORDER BY order_date DESC;


-- ============================================================================
-- SECTION 12: METADATA AND DOCUMENTATION PATTERNS
-- ============================================================================

-- Pattern 1: Document Data Dictionary
CREATE TABLE IF NOT EXISTS sales_prod.curated.data_dictionary (
    table_name STRING NOT NULL,
    column_name STRING NOT NULL,
    data_type STRING,
    description STRING,
    business_logic STRING,
    example_values STRING,
    is_pii BOOLEAN,
    created_date DATE,
    updated_date DATE
);

-- Insert data dictionary entries
INSERT INTO sales_prod.curated.data_dictionary VALUES
('orders_silver', 'order_id', 'STRING', 'Unique order identifier', 'Generated from order_id and order_date', '123e4567-e89b-12d3-a456-426614174000', FALSE, CURRENT_DATE(), CURRENT_DATE()),
('orders_silver', 'customer_id', 'STRING', 'Customer identifier', 'From source system', 'CUST_12345', FALSE, CURRENT_DATE(), CURRENT_DATE()),
('orders_silver', 'order_amount', 'DECIMAL(15,2)', 'Order total amount', 'Sum of item amounts before tax', '99.99', FALSE, CURRENT_DATE(), CURRENT_DATE()),
('orders_silver', 'customer_email', 'STRING', 'Customer email', 'From customer master', 'john@example.com', TRUE, CURRENT_DATE(), CURRENT_DATE());


-- Query data dictionary
SELECT 
    table_name,
    column_name,
    data_type,
    description,
    is_pii
FROM sales_prod.curated.data_dictionary
WHERE table_name = 'orders_silver'
ORDER BY column_name;


-- ============================================================================
-- END OF PATTERNS FILE
-- ============================================================================
