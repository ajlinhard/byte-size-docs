"""
Database Information Schema Comparison Utility

This module provides functions to extract and compare database schemas
from PostgreSQL databases using SQLAlchemy and Polars.
"""

import polars as pl
from sqlalchemy import create_engine, text
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus


def get_db_schemas(
    host: str,
    database: str,
    user: str,
    password: str,
    port: int = 5432,
    schema_name: Optional[str] = None
) -> pl.DataFrame:
    """
    Connect to a PostgreSQL database and retrieve information schema as a Polars DataFrame.
    
    Args:
        host: Database host address
        database: Database name
        user: Database user
        password: Database password
        port: Database port (default: 5432)
        schema_name: Specific schema to filter (default: None, returns all non-system schemas)
    
    Returns:
        Polars DataFrame containing columns, tables, and data types information
    """
    # Create connection string with URL-encoded password
    encoded_password = quote_plus(password)
    connection_string = f"postgresql://{user}:{encoded_password}@{host}:{port}/{database}"
    
    # Create SQLAlchemy engine
    engine = create_engine(connection_string)
    
    # SQL query to get information schema
    query = """
        SELECT 
            table_schema,
            table_name,
            column_name,
            ordinal_position,
            data_type,
            character_maximum_length,
            numeric_precision,
            numeric_scale,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
    """
    
    # Add schema filter if specified
    if schema_name:
        query += f" AND table_schema = '{schema_name}'"
    
    query += " ORDER BY table_schema, table_name, ordinal_position"
    
    try:
        # Execute query and load into Polars DataFrame
        with engine.connect() as conn:
            df = pl.read_database(query=query, connection=conn, infer_schema_length=1000)
        
        return df
    
    finally:
        engine.dispose()


def compare_schemas(
    db1_config: Dict[str, any],
    db2_config: Dict[str, any],
    schema_name: Optional[str] = None,
    export_path: Optional[str] = None
) -> Dict[str, pl.DataFrame]:
    """
    Compare schemas from two different databases.
    
    Args:
        db1_config: Dictionary with connection parameters for first database
                   (host, database, user, password, port)
        db2_config: Dictionary with connection parameters for second database
        schema_name: Specific schema to compare (optional)
        export_path: Path to export the comparison to a csv file (optional)
    Returns:
        Dictionary containing:
            - 'db1_only': Tables/columns only in database 1
            - 'db2_only': Tables/columns only in database 2
            - 'common': Tables/columns in both databases
            - 'differences': Columns with different data types
            - 'db1_schema': Full schema from database 1
            - 'db2_schema': Full schema from database 2
    """
    # Get schemas from both databases
    print("Fetching schema from database 1...")
    df1 = get_db_schemas(**db1_config, schema_name=schema_name)
    
    print("Fetching schema from database 2...")
    df2 = get_db_schemas(**db2_config, schema_name=schema_name)
    
    # Create composite keys for comparison
    key_cols = ['table_schema', 'table_name_clean', 'column_name']
    df1 = df1.with_columns(pl.col('table_name').str.replace('_', '').alias('table_name_clean'))
    df2 = df2.with_columns(pl.col('table_name').str.replace('_', '').alias('table_name_clean'))
    
    df1_keys = df1.select(key_cols).with_columns(
        pl.concat_str(key_cols, separator='.').alias('key')
    )
    df2_keys = df2.select(key_cols).with_columns(
        pl.concat_str(key_cols, separator='.').alias('key')
    )
    

    # Add a composite key to original dataframe for joining
    df1_with_key = df1.with_columns(
        pl.concat_str(key_cols, separator='.').alias('key')
    )
    df2_with_key = df2.with_columns(
        pl.concat_str(key_cols, separator='.').alias('key')
    )
    
    # Find differences
    keys1 = set(df1_keys['key'].to_list())
    keys2 = set(df2_keys['key'].to_list())
    
    only_in_db1 = keys1 - keys2
    only_in_db2 = keys2 - keys1
    common_keys = keys1 & keys2
    
    # Get dataframes for each category
    db1_only = df1_with_key.filter(pl.col('key').is_in(only_in_db1)).drop('key')
    db2_only = df2_with_key.filter(pl.col('key').is_in(only_in_db2)).drop('key')
    common = df1_with_key.filter(pl.col('key').is_in(common_keys)).drop('key')
    
    # Find columns with different data types
    df1_common = df1_with_key.filter(pl.col('key').is_in(common_keys))
    df2_common = df2_with_key.filter(pl.col('key').is_in(common_keys))
    
    # Join to compare data types
    comparison = df1_with_key.join(
        df2_with_key,
        on='key',
        suffix='_db2',
        how='full'
    ).select([
        pl.coalesce(pl.col('table_schema'), pl.col('table_schema_db2')).alias('table_schema'),
        pl.coalesce(pl.col('table_name'), pl.col('table_name_db2')).alias('table_name'),
        pl.coalesce(pl.col('column_name'), pl.col('column_name_db2')).alias('column_name'),
        # is in db1
        pl.col('key').is_not_null().alias('is_in_db1'),
        # is in db2
        pl.col('key_db2').is_not_null().alias('is_in_db2'),
        pl.col('ordinal_position').alias('db1_ordinal_position'),
        pl.col('ordinal_position_db2').alias('db2_ordinal_position'),
        pl.col('data_type').alias('db1_data_type'),
        pl.col('data_type_db2').alias('db2_data_type'),
        pl.col('character_maximum_length').alias('db1_char_max_length'),
        pl.col('character_maximum_length_db2').alias('db2_char_max_length'),
        pl.col('numeric_precision').alias('db1_numeric_precision'),
        pl.col('numeric_precision_db2').alias('db2_numeric_precision')
    ])

    # export to csv if export_path is provided
    if export_path:
        comparison.write_csv(export_path)
        print(f"Comparison exported to {export_path}")
    
    # Print summary
    print("\n" + "="*70)
    print("SCHEMA COMPARISON SUMMARY")
    print("="*70)
    print(f"Total tables/columns in DB1: {len(df1)}")
    print(f"Total tables/columns in DB2: {len(df2)}")
    print(f"Columns only in DB1: {len(db1_only)}")
    print(f"Columns only in DB2: {len(db2_only)}")
    print(f"Common columns: {len(common)}")
    print(f"Columns with different data types: {len(comparison)}")
    print("="*70 + "\n")
    
    return {
        'db1_only': db1_only,
        'db2_only': db2_only,
        'common': common,
        'differences': comparison,
        'db1_schema': df1,
        'db2_schema': df2
    }


def get_table_summary(schema_df: pl.DataFrame) -> pl.DataFrame:
    """
    Get a summary of tables and their column counts.
    
    Args:
        schema_df: DataFrame from get_db_schemas
    
    Returns:
        DataFrame with table summaries
    """
    return schema_df.group_by(['table_schema', 'table_name']).agg([
        pl.count('column_name').alias('column_count'),
        pl.col('column_name').sort_by('ordinal_position').alias('columns')
    ]).sort(['table_schema', 'table_name'])


# Example usage
if __name__ == "__main__":
    # Example configuration
    db1_config = {
        'host': 'postgres-va-claim-tracking.cakhbszocobl.us-gov-east-1.rds.amazonaws.com',
        'database': 'claim_tracking',
        'user': 'postgres',
        'password': '#Lqtq5ASr6WYA90#XQc1_r(.)nAo',
        'port': 5432
    }
    
    db2_config = {
        'host': 'postgres-va-claim-tracking.cakhbszocobl.us-gov-east-1.rds.amazonaws.com',
        'database': 'claim_tracking_new',
        'user': 'postgres',
        'password': '#Lqtq5ASr6WYA90#XQc1_r(.)nAo',
        'port': 5432
    }
    
    # Get schema from single database
    schema = get_db_schemas(**db1_config)
    print(schema)
    
    # Compare two databases
    export_csv_path = r'C:\Users\AndrewLinhard\Documents\Projects\20251125_Schema_Rework\api_vs_app_comparison_results.csv'
    results = compare_schemas(db1_config, db2_config, export_path=export_csv_path)
    
    # Access specific results
    # print("\nColumns only in DB1:")
    # print(results['db1_only'])
    
    # print("\nColumns with different data types:")
    # print(results['differences'])
    
    # Get table summary
    # summary = get_table_summary(results['db1_schema'])
    # print("\nTable Summary:")
    # print(summary)
    
    print("Schema comparison utility loaded. Uncomment examples above to use.")
