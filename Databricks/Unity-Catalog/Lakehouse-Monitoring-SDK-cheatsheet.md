# Databricks Lakehouse Monitoring Python SDK Cheatsheet
Here is a comprehensive cheatsheet for Databricks lakehouse monitoring using the Python SDK. This will cover all the essential operations and configurations you'll need. The cheatsheet includes:

**Key Sections:**
- Setup and authentication
- Core CRUD operations for monitors
- Monitor run management and refresh operations
- Different monitoring types (time series, snapshot, inference log)
- Custom metrics examples
- Schedule and notification configurations
- Working with monitor output tables
- Error handling and best practices
- Bulk operations and utilities

**Practical Features:**
- Real code examples you can copy and modify
- Common patterns for production use
- Error handling strategies
- Configuration validation helpers
- Quick reference tables for methods and cron expressions

The cheatsheet covers everything from basic monitor creation to advanced configurations with custom metrics, and includes practical utilities for managing monitors at scale. You can use this as a reference for implementing lakehouse monitoring programmatically in your data pipelines and workflows.

## Quick Reference

| Operation | Method | Key Parameters |
|-----------|--------|----------------|
| Create Monitor | `w.quality_monitors.create()` | `table_name`, `assets_dir`, `output_schema_name` |
| Get Monitor | `w.quality_monitors.get()` | `table_name` |
| Update Monitor | `w.quality_monitors.update()` | `table_name` + config fields |
| Delete Monitor | `w.quality_monitors.delete()` | `table_name` |
| List Monitors | `w.quality_monitors.list()` | Optional: `max_results` |
| Run Refresh | `w.quality_monitors.run_refresh()` | `table_name` |
| Get Refresh | `w.quality_monitors.get_refresh()` | `table_name`, `refresh_id` |
| List Refreshes | `w.quality_monitors.list_refreshes()` | `table_name` |
| Cancel Refresh | `w.quality_monitors.cancel_refresh()` | `table_name`, `refresh_id` |

## Common Cron Expressions

| Schedule | Cron Expression |
|----------|----------------|
| Every 15 minutes | `0 */15 * * * ?` |
| Hourly | `0 0 * * * ?` |
| Daily at 2 AM | `0 0 2 * * ?` |
| Weekly (Monday 6 AM) | `0 0 6 ? * MON` |
| Monthly (1st at midnight) | `0 0 0 1 * ?` |

## Setup & Authentication

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import *
import pandas as pd
from datetime import datetime, timedelta

# Initialize client (uses default authentication)
w = WorkspaceClient()

# Or with explicit authentication
w = WorkspaceClient(
    host="https://your-workspace.cloud.databricks.com",
    token="your-access-token"
)
```

## Core Monitoring Operations

### 1. Create Monitor

```python
# Basic monitor creation
monitor_info = w.quality_monitors.create(
    table_name="catalog.schema.table_name",
    assets_dir="/path/to/assets",  # Where monitoring assets are stored
    output_schema_name="monitoring_schema"  # Schema for monitoring tables
)

# Advanced monitor with custom configuration
monitor_info = w.quality_monitors.create(
    table_name="catalog.schema.table_name",
    assets_dir="/path/to/monitoring/assets",
    output_schema_name="monitoring_schema",
    
    # Data classification config
    data_classification_config=DataClassificationConfig(
        enabled=True
    ),
    
    # Custom metrics
    custom_metrics=[
        MonitorMetric(
            type=MonitorMetricType.CUSTOM_METRIC_TYPE_AGGREGATE,
            name="avg_price",
            definition="avg(price)",
            output_data_type="double"
        )
    ],
    
    # Inference log configuration (for ML models)
    inference_log=MonitorInferenceLog(
        granularities=["1 hour", "1 day"],
        model_id_col="model_id",
        prediction_col="prediction",
        timestamp_col="timestamp",
        problem_type=MonitorInferenceLogProblemType.PROBLEM_TYPE_REGRESSION
    ),
    
    # Snapshot configuration
    snapshot=MonitorSnapshot(),
    
    # Time series configuration
    time_series=MonitorTimeSeries(
        granularities=["1 hour", "1 day"],
        timestamp_col="timestamp"
    ),
    
    # Schedule
    schedule=MonitorCronSchedule(
        quartz_cron_expression="0 0 12 * * ?"  # Daily at noon
    ),
    
    # Notifications
    notifications=MonitorNotifications(
        on_failure=MonitorNotificationsOnFailure(
            email_addresses=["admin@company.com"]
        )
    ),
    
    # Baseline table for comparison
    baseline_table_name="catalog.schema.baseline_table"
)
```

### 2. Get Monitor Information

```python
# Get monitor details
monitor = w.quality_monitors.get(table_name="catalog.schema.table_name")

print(f"Monitor Status: {monitor.status}")
print(f"Assets Directory: {monitor.assets_dir}")
print(f"Output Schema: {monitor.output_schema_name}")
print(f"Dashboard ID: {monitor.dashboard_id}")
```

### 3. Update Monitor

```python
# Update monitor configuration
updated_monitor = w.quality_monitors.update(
    table_name="catalog.schema.table_name",
    
    # Update schedule
    schedule=MonitorCronSchedule(
        quartz_cron_expression="0 0 */6 * * ?"  # Every 6 hours
    ),
    
    # Update notifications
    notifications=MonitorNotifications(
        on_failure=MonitorNotificationsOnFailure(
            email_addresses=["admin@company.com", "team@company.com"]
        )
    ),
    
    # Add custom metrics
    custom_metrics=[
        MonitorMetric(
            type=MonitorMetricType.CUSTOM_METRIC_TYPE_AGGREGATE,
            name="null_percentage",
            definition="sum(case when col1 is null then 1 else 0 end) * 100.0 / count(*)",
            output_data_type="double"
        )
    ]
)
```

### 4. Delete Monitor

```python
# Delete a monitor
w.quality_monitors.delete(table_name="catalog.schema.table_name")
```

### 5. List Monitors

```python
# List all monitors
monitors = w.quality_monitors.list()
for monitor in monitors:
    print(f"Table: {monitor.table_name}, Status: {monitor.status}")

# List monitors with pagination
monitors_page = w.quality_monitors.list(max_results=10)
```

## Monitor Runs & Refresh

### 1. Run Monitor Refresh

```python
# Trigger manual refresh
refresh_info = w.quality_monitors.run_refresh(
    table_name="catalog.schema.table_name"
)

print(f"Refresh ID: {refresh_info.refresh_id}")
```

### 2. Get Refresh Information

```python
# Get refresh status
refresh = w.quality_monitors.get_refresh(
    table_name="catalog.schema.table_name",
    refresh_id="refresh_id_here"
)

print(f"Refresh State: {refresh.state}")
print(f"Start Time: {refresh.start_time}")
print(f"End Time: {refresh.end_time}")
```

### 3. List Refreshes

```python
# List recent refreshes
refreshes = w.quality_monitors.list_refreshes(
    table_name="catalog.schema.table_name"
)

for refresh in refreshes:
    print(f"Refresh ID: {refresh.refresh_id}, State: {refresh.state}")
```

### 4. Cancel Refresh

```python
# Cancel running refresh
w.quality_monitors.cancel_refresh(
    table_name="catalog.schema.table_name",
    refresh_id="refresh_id_here"
)
```

## Monitor Configuration Types

### Time Series Monitoring

```python
monitor_info = w.quality_monitors.create(
    table_name="catalog.schema.events_table",
    assets_dir="/monitoring/events",
    output_schema_name="events_monitoring",
    
    time_series=MonitorTimeSeries(
        timestamp_col="event_timestamp",
        granularities=["5 minutes", "1 hour", "1 day"]
    )
)
```

### Snapshot Monitoring

```python
monitor_info = w.quality_monitors.create(
    table_name="catalog.schema.batch_table",
    assets_dir="/monitoring/batch",
    output_schema_name="batch_monitoring",
    
    snapshot=MonitorSnapshot()
)
```

### Inference Log Monitoring (ML Models)

```python
monitor_info = w.quality_monitors.create(
    table_name="catalog.schema.model_predictions",
    assets_dir="/monitoring/ml",
    output_schema_name="ml_monitoring",
    
    inference_log=MonitorInferenceLog(
        granularities=["1 hour", "1 day"],
        model_id_col="model_version",
        prediction_col="prediction",
        timestamp_col="prediction_timestamp",
        problem_type=MonitorInferenceLogProblemType.PROBLEM_TYPE_CLASSIFICATION,
        label_col="actual_label"  # For comparing predictions vs actuals
    )
)
```

## Custom Metrics Examples

### Aggregate Metrics

```python
custom_metrics = [
    # Null percentage
    MonitorMetric(
        type=MonitorMetricType.CUSTOM_METRIC_TYPE_AGGREGATE,
        name="null_percentage_col1",
        definition="sum(case when col1 is null then 1 else 0 end) * 100.0 / count(*)",
        output_data_type="double"
    ),
    
    # Duplicate count
    MonitorMetric(
        type=MonitorMetricType.CUSTOM_METRIC_TYPE_AGGREGATE,
        name="duplicate_count",
        definition="sum(cnt - 1) from (select count(*) as cnt from __TABLE__ group by id having count(*) > 1)",
        output_data_type="long"
    ),
    
    # Average value within range
    MonitorMetric(
        type=MonitorMetricType.CUSTOM_METRIC_TYPE_AGGREGATE,
        name="avg_price_in_range",
        definition="avg(case when price between 10 and 1000 then price end)",
        output_data_type="double"
    )
]
```

### Derived Metrics

```python
custom_metrics = [
    # Ratio calculation
    MonitorMetric(
        type=MonitorMetricType.CUSTOM_METRIC_TYPE_DERIVED,
        name="success_rate",
        definition="success_count / total_count * 100",
        output_data_type="double"
    )
]
```

## Schedule Configurations

```python
# Common schedule patterns
schedules = {
    "hourly": MonitorCronSchedule(
        quartz_cron_expression="0 0 * * * ?"
    ),
    "daily_at_2am": MonitorCronSchedule(
        quartz_cron_expression="0 0 2 * * ?"
    ),
    "weekly_monday_6am": MonitorCronSchedule(
        quartz_cron_expression="0 0 6 ? * MON"
    ),
    "every_15_minutes": MonitorCronSchedule(
        quartz_cron_expression="0 */15 * * * ?"
    )
}
```

## Notification Configurations

```python
# Comprehensive notification setup
notifications = MonitorNotifications(
    on_failure=MonitorNotificationsOnFailure(
        email_addresses=["data-team@company.com", "admin@company.com"]
    ),
    on_new_classification_tag_detected=MonitorNotificationsOnNewClassificationTagDetected(
        email_addresses=["security@company.com"]
    )
)
```

## Working with Monitor Output Tables

```python
# After creating a monitor, you can query the output tables
def query_monitor_metrics(table_name: str, output_schema: str):
    """Query monitoring metrics from output tables"""
    
    # Profile metrics table
    profile_table = f"{output_schema}.{table_name.split('.')[-1]}_profile_metrics"
    
    # Query recent metrics
    query = f"""
    SELECT 
        window,
        column_name,
        data_type,
        null_count,
        distinct_count,
        mean,
        std,
        min,
        max
    FROM {profile_table}
    WHERE window >= current_date() - interval 7 days
    ORDER BY window DESC, column_name
    """
    
    return spark.sql(query)

# Get drift metrics
def query_drift_metrics(table_name: str, output_schema: str):
    """Query drift metrics"""
    
    drift_table = f"{output_schema}.{table_name.split('.')[-1]}_drift_metrics"
    
    query = f"""
    SELECT 
        window,
        column_name,
        drift_type,
        drift_score,
        threshold,
        drift_detected
    FROM {drift_table}
    WHERE window >= current_date() - interval 7 days
    AND drift_detected = true
    ORDER BY window DESC, drift_score DESC
    """
    
    return spark.sql(query)
```

## Error Handling & Best Practices

```python
from databricks.sdk.errors import DatabricksError

def create_monitor_safely(table_name: str, config: dict):
    """Safely create a monitor with error handling"""
    try:
        # Check if monitor already exists
        try:
            existing_monitor = w.quality_monitors.get(table_name=table_name)
            print(f"Monitor already exists for {table_name}")
            return existing_monitor
        except DatabricksError as e:
            if "does not exist" in str(e):
                # Monitor doesn't exist, proceed with creation
                pass
            else:
                raise
        
        # Create the monitor
        monitor_info = w.quality_monitors.create(
            table_name=table_name,
            **config
        )
        
        print(f"Monitor created successfully for {table_name}")
        return monitor_info
        
    except DatabricksError as e:
        print(f"Error creating monitor: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

# Usage example
config = {
    "assets_dir": "/monitoring/assets",
    "output_schema_name": "monitoring_schema",
    "time_series": MonitorTimeSeries(
        timestamp_col="timestamp",
        granularities=["1 hour", "1 day"]
    )
}

monitor = create_monitor_safely("catalog.schema.my_table", config)
```

## Monitoring Multiple Tables

```python
def setup_monitoring_for_tables(tables_config: dict):
    """Set up monitoring for multiple tables"""
    
    results = {}
    
    for table_name, config in tables_config.items():
        try:
            print(f"Setting up monitoring for {table_name}...")
            
            monitor = w.quality_monitors.create(
                table_name=table_name,
                **config
            )
            
            # Trigger initial refresh
            refresh = w.quality_monitors.run_refresh(table_name=table_name)
            
            results[table_name] = {
                "status": "success",
                "monitor": monitor,
                "refresh_id": refresh.refresh_id
            }
            
        except Exception as e:
            results[table_name] = {
                "status": "failed",
                "error": str(e)
            }
    
    return results

# Example usage
tables_config = {
    "catalog.schema.sales_data": {
        "assets_dir": "/monitoring/sales",
        "output_schema_name": "sales_monitoring",
        "time_series": MonitorTimeSeries(
            timestamp_col="sale_date",
            granularities=["1 day"]
        )
    },
    "catalog.schema.user_events": {
        "assets_dir": "/monitoring/events",
        "output_schema_name": "events_monitoring",
        "time_series": MonitorTimeSeries(
            timestamp_col="event_timestamp",
            granularities=["1 hour", "1 day"]
        )
    }
}

results = setup_monitoring_for_tables(tables_config)
```

## Common Patterns & Tips

### 1. Monitor Status Checking
```python
def check_monitor_health(table_name: str):
    """Check monitor health and recent runs"""
    
    monitor = w.quality_monitors.get(table_name=table_name)
    refreshes = w.quality_monitors.list_refreshes(table_name=table_name)
    
    latest_refresh = refreshes[0] if refreshes else None
    
    return {
        "monitor_status": monitor.status,
        "latest_refresh_state": latest_refresh.state if latest_refresh else None,
        "last_refresh_time": latest_refresh.end_time if latest_refresh else None
    }
```

### 2. Bulk Operations
```python
def refresh_all_monitors():
    """Refresh all active monitors"""
    
    monitors = w.quality_monitors.list()
    refresh_ids = []
    
    for monitor in monitors:
        if monitor.status == "ACTIVE":
            try:
                refresh = w.quality_monitors.run_refresh(
                    table_name=monitor.table_name
                )
                refresh_ids.append({
                    "table": monitor.table_name,
                    "refresh_id": refresh.refresh_id
                })
            except Exception as e:
                print(f"Failed to refresh {monitor.table_name}: {e}")
    
    return refresh_ids
```

### 3. Configuration Validation
```python
def validate_monitor_config(table_name: str, config: dict):
    """Validate monitor configuration before creation"""
    
    # Check if table exists
    try:
        w.tables.get(full_name=table_name)
    except DatabricksError:
        raise ValueError(f"Table {table_name} does not exist")
    
    # Validate required fields
    required_fields = ["assets_dir", "output_schema_name"]
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate timestamp column if time series monitoring
    if "time_series" in config:
        ts_config = config["time_series"]
        if hasattr(ts_config, "timestamp_col"):
            # Verify timestamp column exists in table
            table_info = w.tables.get(full_name=table_name)
            columns = [col.name for col in table_info.columns]
            if ts_config.timestamp_col not in columns:
                raise ValueError(f"Timestamp column {ts_config.timestamp_col} not found in table")
    
    return True
```
