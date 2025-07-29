
# Lakeflow Declarative Pipelines: An Evolution of Delta Live Tables

Lakeflow Declarative Pipelines is essentially the rebranded and enhanced version of Delta Live Tables (DLT), announced at Databricks' Data + AI Summit in June 2025. Rather than being a separate product, Lakeflow unifies data engineering with Lakeflow Connect, Lakeflow Declarative Pipelines (previously known as DLT), and Lakeflow Jobs (previously known as Workflows). The system comes with advancements on the UI for building an managing pipelines.

<img width="1309" height="580" alt="image" src="https://github.com/user-attachments/assets/81936041-2ed7-4b06-a45d-c6916f5c2401" />

## Key Enhancements and Expansions

**1. Unified Data Engineering Platform**
Lakeflow Declarative Pipelines makes it easy to optimize pipeline performance by declaring an entire incremental data pipeline with streaming tables and materialized views, while being part of a broader unified platform that includes ingestion (Connect) and orchestration (Jobs).

**2. Enhanced Performance and Cost Optimization**
Up to 5x better price/performance for data ingestion and 98% cost savings for complex transformations. The platform now provides better optimization capabilities for both latency and cost depending on pipeline requirements.

**3. Simplified Development Experience**
Develop pipelines in the IDE for Data Engineering without any context switching. See the DAG, data preview and execution insights in one UI. Develop code easily with autocomplete, in-line errors and diagnostics.

**4. Enhanced CDC Capabilities**
Simplify change data capture with the APPLY CHANGES APIs for change data feeds and database snapshots. Lakeflow Declarative Pipelines automatically handles out-of-sequence records for SCD Type 1 and 2, simplifying the hardest parts of CDC.

**5. Broader Source and Sink Support**
Lakeflow Declarative Pipelines supports a broad ecosystem of sources and sinks. Load data from any source — including cloud storage, message buses, change data feeds, databases and enterprise apps.

**6. Advanced Data Quality and Monitoring**
Expectations allow you to guarantee data arriving in tables meets data quality requirements and provides insights on data quality with each pipeline update, with enhanced monitoring capabilities through the event log system.

## Core Capabilities Retained from DLT

The fundamental declarative approach remains the same - simply declare the data transformations you need — let Lakeflow Declarative Pipelines handle the rest. It still provides:

- Automatic dependency management and scaling
- Built-in data quality controls
- Support for both batch and streaming processing
- Integration with Unity Catalog and Delta Lake
- Incremental processing with checkpointing

## Bottom Line

Lakeflow Declarative Pipelines represents the natural evolution of Delta Live Tables, expanding it from a pipeline framework into part of a comprehensive data engineering platform while adding significant performance improvements, enhanced development experience, and broader connectivity options. If you're currently using DLT, the transition to Lakeflow Declarative Pipelines should be seamless while providing these additional benefits.

## Lakeflow Declarative Pipelines UI

<img width="1302" height="555" alt="image" src="https://github.com/user-attachments/assets/e9689bd3-383e-4fc2-bbd0-211a1c939c89" />

### Common Pipelines Settings
- Databricks recommends developing new pipelines with severless compute.
  - Optimizes cost whiles maintaining performance.
  - Serverless compute includes potential incremental materialized view refresh.
  - Focus on code over cluster settings, with option for time-sensitive workload optimization.
- Code Assets
  - Pipelines Root Folder - automatically includes all relevant files in the folder and adds the path to sys.path in python. Can be a git folder.
  - Source Code folder - section of files and subfolders for files related to the pipeline code. (.py, .sql, notebooks)
  - You can add additional paths outside the root folder for source, but its not recommend for organizational and permission reasons.
- Configuration Parameters
  - A key values pair for parameters needed throughout the pipelines.
  - In code the values is replaced with ${param name}.
 
  ### Other Settings
  - Pipeline ID, Pipeline Type, Pipeline Name, Creator, Owner
  - Enviornment which allows you to import packages, code, and files into the runtime environment.
  - Tags for helping with logging and assigning cost.
  - Budget - a tool for blocking the pipeline for running too much data through or warnings.
  - Notifications - send emails to specific users based on results.
  - Advance settings
    - Pipeline Mode - choose continuous or triggered for executing the pipeline as near realtime or as incremental batches.
    - Channel - the version of the databricks runtime to execute.
    - Event Logs - publish the events in the pipeline to a metastore.
 
### Run Options
Most of the different run options are for different parts of testing, but have use cases in production as well.
- Dry Run, checks if the setup of your pipeline has any glaring issues: bad or missing parameters, unknown data, looping dependencies etc.
- Run Pipeline (Manual), will execute your pipeline using the incremental settings.
- Run Pipeline with full table refresh, will re-execute all tables wiping out delta table history, edits, and data.
  - Note: If tables are sourcing from S3 or file sources where there is cleanup data could be LOST!
- Scheduled, allowing to run the pipeline on crontab type schedules.
