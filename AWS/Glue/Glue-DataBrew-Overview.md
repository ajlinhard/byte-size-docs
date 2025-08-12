# Glue DataBrew Overview
AWS Glue and AWS Glue DataBrew are related but distinct services within the AWS data ecosystem. DataBrew allows for visual building and representation of Glue data actions and exploration.

Think of them as serving different stages of the data pipeline:

1. **DataBrew** - Data discovery, profiling, and preparation
2. **Glue** - Production ETL processing and orchestration

You might use DataBrew to explore a new dataset, understand its quality issues, and create cleaning recipes. Then export that logic to run in a Glue job for production processing at scale.

### Documentation:
- [AWS DataBrew - Home Page](https://aws.amazon.com/glue/features/databrew/)


# Basic DataBrew Concepts

#### Dataset
In DataBrew, a dataset refers to data that can be obtained from various sources, such as an Amazon S3 file, a supported JDBC data source, or the Data Catalog. The dataset also includes information on how DataBrew can access the data if it is not directly uploaded.

#### Profiling
DataBrew validates data by running a series of evaluations to identify trends and spot any irregularities by accessing data directly from the data lake, data warehouses, and databases.

#### Data lineage
Data lineage is a visual representation of all the data transformations, from origin to target.

#### Data quality
A data-quality process can help ensure the accuracy of your data. You establish a set of guidelines, known as a ruleset, and enforce the data to identify and correct the faulty data. This ruleset includes comparisons between actual data values and desired values. The entire ruleset is considered valid if the criteria set in the ruleset are met. After checking the results of each rule, users can make necessary adjustments to their data. After changes have been made, users can reevaluate the ruleset multiple times.

Examples of rules include the following:
- The value in column APY is between 0 and 100.
- The number of missing values in column group_name doesn't exceed five percent.

#### Recipes
In DataBrew, a recipe is a sequence of operations used to transform the data. The steps in a recipe can be tested on a data sample before being applied to the entire dataset.

#### Project
DataBrew provides a centralized data analysis and manipulation platform through projects. A project consists of two key components:

A dataset that grants read-only access to the source data
A recipe that uses DataBrew transformation actions on the dataset
The DataBrew console and interface is user friendly and interactive, encouraging exploration and testing of different transformations to evaluate their effects on the data.

#### Jobs
The job feature in DataBrew serves two main functions:

A DataBrew recipe job that runs the transformations on a dataset
A DataBrew profile job that inspects a dataset and generates a comprehensive summary of the data
Profile jobs produce their findings to Amazon S3 and offer essential insights to assist in identifying appropriate data preparation actions. Use a DataBrew recipe job to clean and standardize the data in a dataset and output it to a designated location. Running a recipe job does not modify the source data or the dataset. The job accesses the source data in a read-only manner, and the output is sent to the specified location on Amazon S3, the Data Catalog, or a supported JDBC database.

#### File type
DataBrew supports specific file types and formats, including comma-separated values (CSV), Microsoft Excel workbook, JSON documents and JSON lines, Apache Optimized Row Columnar (ORC), and Apache Parquet format.

#### Transform
Transform is the set of instructions or algorithms used to transform your data into a different format.

# Glue Core vs DataBrew

## AWS Glue (Core Service)
AWS Glue is a fully managed ETL (Extract, Transform, Load) service that handles:
- **Data cataloging** - Automatically discovers and catalogs your data
- **ETL job creation** - Writes and runs Apache Spark or Python shell scripts
- **Schema inference** - Automatically detects data schemas
- **Code generation** - Can auto-generate ETL code
- **Job scheduling** - Runs jobs on a schedule or trigger-based

## AWS Glue DataBrew
DataBrew is a visual data preparation service that's part of the broader Glue family:
- **No-code interface** - Visual point-and-click data preparation
- **Data profiling** - Automatic data quality assessment and statistics
- **Recipe-based transformations** - Pre-built transformation functions
- **Interactive exploration** - Browse and understand your data before transforming
- **ML-powered suggestions** - Recommends transformations based on data patterns

## Key Differences

**Glue** requires coding knowledge (Python/Scala) and is better for:
- Complex ETL pipelines
- Large-scale distributed processing
- Custom ETL logic and complex transformations
- Integration with data lakes and warehouses
- Production-grade pipeline orchestration
- Integration with other AWS services

**DataBrew** is code-free and excels at:
- Interactive data exploration and profiling
- Row-by-row data quality assessment
- Statistical analysis and anomaly detection
- Pre-built transformation functions (recipes)
- Quick data cleaning tasks
- Business user-friendly operations
- Standardized transformations

## Key Architectural Differences

**DataBrew's unique features:**
- Built-in data profiling with 40+ statistical measures
- Visual data quality assessment (nulls, duplicates, outliers)
- Interactive sampling for large datasets
- Recipe-based transformation library
- Column-level lineage tracking

**Regular Glue capabilities DataBrew doesn't replicate:**
- Custom Spark transformations
- Complex joins across multiple large datasets
- Advanced partitioning strategies
- Integration with Glue Catalog crawlers
- Custom Python/Scala libraries

## Is DataBrew Required?

**No, DataBrew is not required** for jobs, automation, and transformations. You can accomplish all ETL tasks using core AWS Glue alone. However, DataBrew is commonly used for it offers benefits:

- **Faster prototyping** - Quickly explore and clean data without writing code
- **Business user accessibility** - Non-technical users can perform data prep
- **Data quality insights** - Built-in profiling shows data issues upfront
- **Recipe reusability** - Save transformation recipes for consistent processing

Choose based on your team's technical skills, complexity requirements, and preference for visual vs. code-based workflows. Many organizations use both: DataBrew for initial exploration and simple transformations, then Glue for complex production ETL pipelines.

