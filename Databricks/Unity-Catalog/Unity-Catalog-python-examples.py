"""
Databricks Unity Catalog - Advanced Python Examples
Comprehensive code patterns for real-world implementations
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType, DecimalType, TimestampType
from pyspark.sql.functions import col, when, desc, count, current_timestamp, date_format
from typing import List, Dict, Tuple
import logging

# Initialize Spark Session
spark = SparkSession.builder.appName("UnityC atalogExamples").getOrCreate()
logger = logging.getLogger(__name__)


# ============================================================================
# PART 1: BASIC OPERATIONS
# ============================================================================

class UnityC atalogBasics:
    """Basic Unity Catalog operations"""
    
    @staticmethod
    def create_catalog_structure(catalog_name: str, schemas: List[str]) -> bool:
        """Create a catalog with multiple schemas"""
        try:
            # Create catalog
            spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog_name}")
            logger.info(f"Created catalog: {catalog_name}")
            
            # Create schemas
            for schema in schemas:
                spark.sql(f"""
                    CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema}
                    COMMENT = '{schema} layer data'
                """)
                logger.info(f"Created schema: {catalog_name}.{schema}")
            
            return True
        except Exception as e:
            logger.error(f"Error creating catalog structure: {str(e)}")
            return False
    
    @staticmethod
    def create_managed_table(catalog: str, schema: str, table_name: str, 
                            schema_def: StructType) -> bool:
        """Create a managed table with schema definition"""
        try:
            full_path = f"{catalog}.{schema}.{table_name}"
            
            # Create empty DataFrame with specified schema
            df = spark.createDataFrame([], schema_def)
            
            # Write as managed table
            df.write.mode("overwrite").option("mergeSchema", "true") \
                .format("delta") \
                .saveAsTable(full_path)
            
            logger.info(f"Created managed table: {full_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating table: {str(e)}")
            return False
    
    @staticmethod
    def register_external_table(catalog: str, schema: str, table_name: str, 
                               location: str) -> bool:
        """Register an external table from cloud storage"""
        try:
            full_path = f"{catalog}.{schema}.{table_name}"
            
            spark.sql(f"""
                CREATE TABLE IF NOT EXISTS {full_path}
                LOCATION '{location}'
                USING DELTA
            """)
            
            logger.info(f"Registered external table: {full_path}")
            return True
        except Exception as e:
            logger.error(f"Error registering external table: {str(e)}")
            return False
    
    @staticmethod
    def list_all_objects(catalog: str) -> Dict[str, List[str]]:
        """List all schemas and tables in a catalog"""
        try:
            result = {}
            
            # Get schemas
            schemas = spark.sql(f"SHOW SCHEMAS IN {catalog}").collect()
            
            for schema_row in schemas:
                schema_name = schema_row[0]
                
                # Get tables in schema
                tables = spark.sql(f"""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_catalog = '{catalog}' 
                    AND table_schema = '{schema_name}'
                """).collect()
                
                result[schema_name] = [t[0] for t in tables]
            
            return result
        except Exception as e:
            logger.error(f"Error listing objects: {str(e)}")
            return {}


# ============================================================================
# PART 2: PERMISSION AND GOVERNANCE MANAGEMENT
# ============================================================================

class UnityC atalogPermissions:
    """Manage permissions and access control"""
    
    @staticmethod
    def create_group_and_grant_permissions(group_name: str, 
                                          permissions: Dict[str, str]) -> bool:
        """
        Create a group and grant permissions
        
        permissions: {
            'catalog.schema.table': 'SELECT',
            'catalog.schema': 'USAGE'
        }
        """
        try:
            # Create group
            spark.sql(f"CREATE GROUP IF NOT EXISTS `{group_name}`")
            logger.info(f"Created group: {group_name}")
            
            # Grant permissions
            for resource, privilege in permissions.items():
                if '.' in resource:
                    parts = resource.split('.')
                    if len(parts) == 3:
                        object_type = "TABLE"
                    elif len(parts) == 2:
                        object_type = "SCHEMA"
                    else:
                        object_type = "CATALOG"
                else:
                    object_type = "CATALOG"
                
                spark.sql(f"""
                    GRANT {privilege} ON {object_type} `{resource}` 
                    TO `{group_name}`
                """)
                logger.info(f"Granted {privilege} on {resource} to {group_name}")
            
            return True
        except Exception as e:
            logger.error(f"Error setting up permissions: {str(e)}")
            return False
    
    @staticmethod
    def get_object_permissions(object_path: str) -> DataFrame:
        """Get all permissions on a specific object"""
        try:
            # Determine object type
            parts = object_path.split('.')
            if len(parts) == 3:
                object_type = "TABLE"
            elif len(parts) == 2:
                object_type = "SCHEMA"
            else:
                object_type = "CATALOG"
            
            result = spark.sql(f"""
                SHOW GRANTS ON {object_type} `{object_path}`
            """)
            
            return result
        except Exception as e:
            logger.error(f"Error retrieving permissions: {str(e)}")
            return None
    
    @staticmethod
    def audit_access_patterns(catalog: str, days: int = 7) -> DataFrame:
        """Analyze access patterns across catalog"""
        try:
            df = spark.sql(f"""
                SELECT 
                    DATE(timestamp) as access_date,
                    user_identity.email as user_email,
                    action,
                    object_name,
                    COUNT(*) as access_count
                FROM system.access.audit
                WHERE object_type IN ('TABLE', 'SCHEMA', 'CATALOG')
                    AND timestamp >= CURRENT_DATE() - {days}
                GROUP BY DATE(timestamp), user_email, action, object_name
                ORDER BY access_date DESC, access_count DESC
            """)
            
            return df
        except Exception as e:
            logger.error(f"Error getting audit data: {str(e)}")
            return None


# ============================================================================
# PART 3: DATA QUALITY AND CLASSIFICATION
# ============================================================================

class DataQualityManager:
    """Manage data quality and classification"""
    
    @staticmethod
    def tag_sensitive_columns(catalog: str, schema: str, table: str, 
                             column_classifications: Dict[str, str]) -> bool:
        """
        Apply sensitivity tags to columns
        
        column_classifications: {
            'email': 'pii',
            'salary': 'confidential',
            'phone': 'pii'
        }
        """
        try:
            table_path = f"{catalog}.{schema}.{table}"
            
            for col_name, classification in column_classifications.items():
                spark.sql(f"""
                    ALTER TABLE {table_path}
                    ALTER COLUMN {col_name}
                    SET TAG data_classification = '{classification}'
                """)
                logger.info(f"Tagged {col_name} as {classification}")
            
            return True
        except Exception as e:
            logger.error(f"Error tagging columns: {str(e)}")
            return False
    
    @staticmethod
    def scan_table_quality(catalog: str, schema: str, table: str) -> Dict:
        """
        Scan table for quality metrics
        Returns statistics about data completeness, uniqueness, etc.
        """
        try:
            table_path = f"{catalog}.{schema}.{table}"
            df = spark.table(table_path)
            
            quality_report = {
                'table': table_path,
                'row_count': df.count(),
                'column_count': len(df.columns),
                'column_details': {}
            }
            
            for col_name in df.columns:
                col_analysis = spark.sql(f"""
                    SELECT 
                        COUNT(*) as total_rows,
                        COUNT({col_name}) as non_null_count,
                        COUNT(DISTINCT {col_name}) as distinct_count,
                        ROUND(COUNT({col_name})/COUNT(*)*100, 2) as completeness_pct
                    FROM {table_path}
                """).collect()[0]
                
                quality_report['column_details'][col_name] = {
                    'non_null_count': col_analysis[1],
                    'distinct_count': col_analysis[2],
                    'completeness_pct': col_analysis[3]
                }
            
            return quality_report
        except Exception as e:
            logger.error(f"Error scanning table quality: {str(e)}")
            return {}
    
    @staticmethod
    def create_quality_monitoring_view(catalog: str, schema: str, 
                                      table: str) -> bool:
        """Create a view for monitoring data quality"""
        try:
            table_path = f"{catalog}.{schema}.{table}"
            view_name = f"{catalog}.{schema}.{table}_quality_monitor"
            
            spark.sql(f"""
                CREATE OR REPLACE VIEW {view_name} AS
                SELECT 
                    CURRENT_DATE() as quality_check_date,
                    COUNT(*) as row_count,
                    COUNT(DISTINCT {table}_id) as unique_records,
                    ROUND(100.0 * COUNT(*) / LAG(COUNT(*)) 
                          OVER (ORDER BY CURRENT_DATE()), 2) as row_count_change_pct
                FROM {table_path}
            """)
            
            logger.info(f"Created quality monitor view: {view_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating quality view: {str(e)}")
            return False


# ============================================================================
# PART 4: ADVANCED SECURITY - ROW AND COLUMN LEVEL
# ============================================================================

class AdvancedSecurity:
    """Implement row-level and column-level security"""
    
    @staticmethod
    def setup_column_masking(catalog: str, schema: str, table: str,
                            mask_config: Dict[str, str]) -> bool:
        """
        Set up column masking functions and apply them
        
        mask_config: {
            'email': 'CASE WHEN is_account_group_member(\"admin\") THEN email ELSE \"***@***.com\" END',
            'ssn': 'CASE WHEN is_account_group_member(\"hr\") THEN ssn ELSE \"XXX-XX-XXXX\" END'
        }
        """
        try:
            table_path = f"{catalog}.{schema}.{table}"
            
            for col_name, mask_logic in mask_config.items():
                # Create masking function
                func_name = f"{schema}_{table}_{col_name}_mask"
                
                spark.sql(f"""
                    CREATE OR REPLACE FUNCTION {catalog}.{schema}.{func_name}({col_name} STRING)
                    RETURNS STRING
                    LANGUAGE SQL
                    AS $$
                        {mask_logic}
                    $$
                """)
                
                # Apply mask to column
                spark.sql(f"""
                    ALTER TABLE {table_path}
                    ALTER COLUMN {col_name}
                    SET MASK {catalog}.{schema}.{func_name}()
                """)
                
                logger.info(f"Applied masking to {col_name} in {table_path}")
            
            return True
        except Exception as e:
            logger.error(f"Error setting up column masking: {str(e)}")
            return False
    
    @staticmethod
    def setup_row_filtering(catalog: str, schema: str, table: str,
                           filter_logic: str) -> bool:
        """
        Apply row-level filtering to table
        
        Example filter_logic:
        CASE 
            WHEN is_account_group_member('na_sales') AND region = 'NA' THEN TRUE
            WHEN is_account_group_member('eu_sales') AND region = 'EU' THEN TRUE
            ELSE FALSE
        END
        """
        try:
            table_path = f"{catalog}.{schema}.{table}"
            
            # Create filter function
            func_name = f"{schema}_{table}_row_filter"
            
            spark.sql(f"""
                CREATE OR REPLACE FUNCTION {catalog}.{schema}.{func_name}()
                RETURNS BOOLEAN
                LANGUAGE SQL
                AS $$
                    {filter_logic}
                $$
            """)
            
            # Apply filter to table
            spark.sql(f"""
                ALTER TABLE {table_path}
                ADD ROW FILTER {catalog}.{schema}.{func_name}() ON ()
            """)
            
            logger.info(f"Applied row filtering to {table_path}")
            return True
        except Exception as e:
            logger.error(f"Error setting up row filtering: {str(e)}")
            return False
    
    @staticmethod
    def create_dynamic_view(view_name: str, table_path: str, 
                           security_rules: str) -> bool:
        """
        Create a dynamic view with embedded security rules
        
        Example security_rules:
        CASE 
            WHEN is_account_group_member('managers') THEN salary
            ELSE 0
        END AS salary
        """
        try:
            spark.sql(f"""
                CREATE OR REPLACE VIEW {view_name} AS
                SELECT 
                    *,
                    {security_rules}
                FROM {table_path}
            """)
            
            logger.info(f"Created dynamic view: {view_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating dynamic view: {str(e)}")
            return False


# ============================================================================
# PART 5: LINEAGE AND AUDIT TRACKING
# ============================================================================

class LineageAuditor:
    """Track data lineage and audit trails"""
    
    @staticmethod
    def get_table_lineage(table_path: str) -> Dict:
        """Get upstream and downstream dependencies for a table"""
        try:
            # Get upstream tables
            upstream = spark.sql(f"""
                SELECT DISTINCT upstream_table
                FROM system.lineage.table_lineage
                WHERE downstream_table = '{table_path}'
            """).collect()
            
            # Get downstream tables
            downstream = spark.sql(f"""
                SELECT DISTINCT downstream_table
                FROM system.lineage.table_lineage
                WHERE upstream_table = '{table_path}'
            """).collect()
            
            lineage = {
                'table': table_path,
                'upstream': [row[0] for row in upstream],
                'downstream': [row[0] for row in downstream]
            }
            
            return lineage
        except Exception as e:
            logger.error(f"Error getting lineage: {str(e)}")
            return {}
    
    @staticmethod
    def get_column_lineage(table_path: str) -> DataFrame:
        """Get column-level lineage for a table"""
        try:
            df = spark.sql(f"""
                SELECT 
                    upstream_table,
                    upstream_column,
                    downstream_table,
                    output_column,
                    transformation
                FROM system.lineage.column_lineage
                WHERE downstream_table = '{table_path}'
                ORDER BY upstream_table, upstream_column
            """)
            
            return df
        except Exception as e:
            logger.error(f"Error getting column lineage: {str(e)}")
            return None
    
    @staticmethod
    def get_access_audit_trail(table_path: str, days: int = 30) -> DataFrame:
        """Get audit trail of who accessed what and when"""
        try:
            df = spark.sql(f"""
                SELECT 
                    timestamp,
                    user_identity.email as user_email,
                    action,
                    response.status_code as status,
                    response.result as action_result
                FROM system.access.audit
                WHERE object_name LIKE '%{table_path.split('.')[-1]}%'
                    AND timestamp >= CURRENT_TIMESTAMP() - INTERVAL {days} DAY
                ORDER BY timestamp DESC
            """)
            
            return df
        except Exception as e:
            logger.error(f"Error getting audit trail: {str(e)}")
            return None
    
    @staticmethod
    def get_access_denied_events(catalog: str, days: int = 7) -> DataFrame:
        """Get all denied access attempts"""
        try:
            df = spark.sql(f"""
                SELECT 
                    timestamp,
                    user_identity.email as user_email,
                    action,
                    object_name,
                    object_type,
                    response.error_message as denial_reason
                FROM system.access.audit
                WHERE response.status_code != 200
                    AND timestamp >= CURRENT_TIMESTAMP() - INTERVAL {days} DAY
                    AND object_type NOT IN ('SERVICE_PRINCIPAL', 'TOKEN')
                ORDER BY timestamp DESC
            """)
            
            return df
        except Exception as e:
            logger.error(f"Error getting denied events: {str(e)}")
            return None


# ============================================================================
# PART 6: MEDALLION ARCHITECTURE IMPLEMENTATION
# ============================================================================

class MedallionArchitecture:
    """Implement medallion architecture with UC"""
    
    @staticmethod
    def setup_medallion_catalogs(project_name: str, 
                                environments: List[str] = ['dev', 'prod']) -> bool:
        """Set up medallion architecture across multiple environments"""
        try:
            medallion_layers = ['raw', 'curated', 'analytics']
            
            for env in environments:
                catalog_name = f"{project_name}_{env}"
                
                # Create catalog
                spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog_name}")
                
                # Create medallion layer schemas
                for layer in medallion_layers:
                    schema_name = f"{layer}_layer"
                    spark.sql(f"""
                        CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema_name}
                        COMMENT = '{layer.upper()} layer - {env.upper()} environment'
                    """)
                
                logger.info(f"Set up medallion architecture for {catalog_name}")
            
            return True
        except Exception as e:
            logger.error(f"Error setting up medallion architecture: {str(e)}")
            return False
    
    @staticmethod
    def ingest_to_bronze(catalog: str, schema: str, table_name: str,
                        df: DataFrame, partition_cols: List[str] = None) -> bool:
        """Ingest raw data to bronze layer"""
        try:
            table_path = f"{catalog}.{schema}.{table_name}"
            
            # Add metadata columns
            df = df.withColumn("_ingested_at", current_timestamp()) \
                   .withColumn("_ingestion_batch_id", col("_ingested_at").cast("string"))
            
            # Write to bronze
            writer = df.write.mode("append").format("delta")
            
            if partition_cols:
                writer = writer.partitionBy(*partition_cols)
            
            writer.option("mergeSchema", "true").mode("overwrite").saveAsTable(table_path)
            
            logger.info(f"Ingested data to bronze: {table_path}")
            return True
        except Exception as e:
            logger.error(f"Error ingesting to bronze: {str(e)}")
            return False
    
    @staticmethod
    def transform_to_silver(catalog: str, bronze_table: str, 
                           silver_table: str,
                           transformations: Dict[str, str] = None) -> bool:
        """
        Transform bronze data to silver layer
        transformations: {'old_column': 'new_expression'}
        """
        try:
            # Read from bronze
            df = spark.table(bronze_table)
            
            # Apply transformations
            if transformations:
                for col_name, expression in transformations.items():
                    df = df.withColumn(col_name, col(expression))
            
            # Add processing metadata
            df = df.withColumn("_processed_at", current_timestamp())
            
            # Remove ingestion metadata columns we no longer need
            df = df.drop("_ingestion_batch_id")
            
            # Write to silver
            df.write.mode("overwrite").format("delta").option("mergeSchema", "true") \
                .saveAsTable(silver_table)
            
            logger.info(f"Transformed data to silver: {silver_table}")
            return True
        except Exception as e:
            logger.error(f"Error transforming to silver: {str(e)}")
            return False


# ============================================================================
# PART 7: USAGE EXAMPLE AND TESTING
# ============================================================================

def example_workflow():
    """Complete example workflow"""
    
    # 1. Setup basic structure
    basics = UnityC atalogBasics()
    basics.create_catalog_structure(
        'sales_prod',
        ['raw_layer', 'curated_layer', 'analytics_layer']
    )
    
    # 2. Create sample table
    schema = StructType([
        StructField("customer_id", IntegerType(), True),
        StructField("email", StringType(), True),
        StructField("salary", DecimalType(10, 2), True),
        StructField("region", StringType(), True),
        StructField("created_at", TimestampType(), True)
    ])
    
    basics.create_managed_table('sales_prod', 'curated_layer', 'customers', schema)
    
    # 3. Setup permissions
    perms = UnityC atalogPermissions()
    perms.create_group_and_grant_permissions(
        'analysts',
        {
            'sales_prod': 'USAGE',
            'sales_prod.curated_layer': 'USAGE',
            'sales_prod.curated_layer.customers': 'SELECT'
        }
    )
    
    # 4. Apply security
    security = AdvancedSecurity()
    security.setup_column_masking(
        'sales_prod',
        'curated_layer',
        'customers',
        {
            'email': 'CASE WHEN is_account_group_member("hr_team") THEN email ELSE "***@company.com" END'
        }
    )
    
    # 5. Tag data
    dq = DataQualityManager()
    dq.tag_sensitive_columns(
        'sales_prod',
        'curated_layer',
        'customers',
        {'email': 'pii', 'salary': 'confidential'}
    )
    
    print("✓ Complete workflow executed successfully")


if __name__ == "__main__":
    # Execute example
    example_workflow()
