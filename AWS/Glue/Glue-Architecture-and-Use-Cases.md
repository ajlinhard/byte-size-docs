# Glue Architecture and Use Cases
With AWS Glue, you can identify and build a technical data catalog for various data storage locations. You can use this data catalog as input and then carry out ETL or extract, load, transform (ELT) processes based on their requirements. The following architecture displays the typical pattern of connecting to data sources using connectors. Later, crawl the data to identify the schema, clean and standardize, and author the ETL process to generate raw data. Then, use the same ETL utilities provided by AWS Glue to create refined data. This data can finally be consumed through analytical query engines like Amazon Athena, Amazon Redshift, and Amazon QuickSight.

<img width="1296" height="705" alt="image" src="https://github.com/user-attachments/assets/95bc46f9-1cf3-4f86-8589-2b8a9ac3d816" />

1. **Data source** - Users can connect to various data sources using AWS Glue. These data sources can be popular relational databases with AWS or outside of Amazon Web Services (AWS). Data sources can also be flat files or streaming sources. AWS Glue uses built-in connectors and crawlers to automatically detect the data type and register the schema in the Data Catalog.
2. **AWS Glue Connecters** - AWS Glue saves connection objects for specific data stores with login credentials, URIs, and virtual private cloud (VPC) details. It supports popular data stores like Amazon Redshift, Amazon Aurora, SQL servers, MySQL, MongoDB, and PostgreSQL through Java Database Connectivity (JDBC) connections, and many more. Users can use marketplace connectors or custom connectors for non-built-in data stores.
3. **AWS Glue crawler** - AWS Glue crawlers use built-in or custom connectors to connect multiple data sources to scan, classify, and extract schema information. The metadata is stored in Data Catalog, which can then be used to build ETL and operationalize the workload.
4. **Data Catalog** -AWS Glue offers a technical metadata store so you can store, classify, and define data schema. Data Catalog tracks metadata changes as data evolves, which you can share with other analytics services. It holds table information, such as schema, properties, and data format. It also works with services like AWS Identity and Access Management (IAM) and AWS Lake Formation to control table and database access.
5. **AWS Glue Schema Registry** - With AWS Glue Schema Registry, you can manage and enforce schemas on your data-streaming applications using convenient integrations. These integrations include Apache Kafka, Amazon MSK, Amazon Kinesis Data Streams, Amazon Kinesis Data Analytics for Apache Flink, and AWS Lambda.
6. **DataBrew** - DataBrew is a visual data preparation tool that helps you clean, enrich, format, and normalize datasets using over 250 built-in transformations. Users can create a recipe for a dataset using the transformations of their choice, and then reuse that recipe repeatedly on different collections of data.
7. **AWS Glue Jobs** - AWS Glue Jobs provides a managed infrastructure for orchestrating ETL workflows. Users can create jobs in AWS Glue that automate their scripts to extract, transform, and transfer data to different locations. These jobs can be scheduled or launched by events, such as the arrival of new data, and they can also be chained together.
8. **Data store and targets** - AWS Glue provides access to various data sources and targets, including Amazon Simple Storage Service (Amazon S3) and databases on AWS or on premises. It can even access any sources that offer JDBC utility for connections. For a full list of supported connections using AWS Glue crawler, see [Which Data Stores Can I Crawl?](https://docs.aws.amazon.com/glue/latest/dg/crawler-data-stores.html)
9. **AWS analytics services** - AWS offers the following analytics services:
  - Athena is an interactive query service that makes it effortless to analyze data in Amazon S3 and data sources. 
  - Amazon Redshift is a fully managed, petabyte-scale data warehouse service in the cloud.
  - QuickSight is a scalable, serverless, embeddable, ML-powered business intelligence (BI).

---
## Common Architectures

### Lambda Architecture
Glue fits into lambda architectures by handling both batch and streaming layers. Batch jobs process historical data from S3, while streaming jobs handle real-time data from Kinesis. Results merge in a serving layer accessible through Athena or Redshift.

### Data Lake Architecture
In data lake patterns, Glue crawlers discover data in S3 and populate the catalog. ETL jobs transform raw data through bronze, silver, and gold layers. The Data Catalog enables querying through multiple engines like Athena, EMR, and Redshift Spectrum.

### Data Warehouse Integration
Glue connects traditional data warehouses with modern analytics. Jobs extract data from sources like RDS or on-premises databases, transform it according to business rules, and load it into Redshift or other targets. This supports hybrid architectures combining traditional and cloud-native approaches.

---
# Basic Technical Concepts
These are the basic technical concepts when working with Glue and can be setup and used through Glue Studio or with in scripts:

#### Connection
An AWS Glue connection is an object in the Data Catalog that holds information such as login credentials, URI strings, VPC details, and more for a specific data store. AWS Glue components, such as crawlers, jobs, and development endpoints, use these connections to access particular data stores. Connections can be used for source and target data stores, and the same connection can be used multiple times by various crawlers or ETL jobs. For more information, see Adding an [AWS Glue Connection](https://docs.aws.amazon.com/glue/latest/dg/console-connections.html).

#### Crawler
An AWS Glue crawler can connect to various sources, identify their schema, and categorize them into data formats. They can also create metadata tables in the Data Catalog by using built-in data classifiers. For more information about crawlers, see [Defining Crawlers in AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/add-crawler.html).

#### Datastore, data source, data target
A data store refers to physical storage where data is meant to persist permanently. An example of data stores in AWS would be Amazon S3 buckets and relational databases like Amazon Relational Database Service (Amazon RDS) for MySQL. These can serve as the input for processing or transformation. A data target refers to a data store where a process or transformation is output-written.

#### AWS Glue interactive sessions
With AWS Glue interactive sessions, users can build and test data preparation needed for analytics applications. These sessions provide self-managed notebooks, which help developers write one-time queries or transformations that can be used to prepare data for ML. AWS Glue interactive sessions offer notebook editors, which can be deployed locally or remotely. Doing it this way can assist developers with quick development and testing time. AWS Glue integrates with AWS Glue Studio and Amazon SageMaker Studio for notebook management. For more information about AWS Glue interactive sessions, see Getting Started with [AWS Glue interactive sessions](https://docs.aws.amazon.com/glue/latest/dg/interactive-sessions.html).

#### DynamicFrame
A DynamicFrame is a distributed table that facilitates the storage of nested data, such as structures and arrays. It does this by cleaning and reorganizing semi-structured datasets like JSON, Avro, and Apache logs. With DynamicFrame, there is no need for an upfront schema. The schema can be inferred without interruption so that transformations occur in a single pass. It is not difficult to handle unexpected changes because it tracks new fields and inconsistent changes in data types with choices, automatically marking and separating error records.

#### Job
The business logic necessary to carry out ETL work consists of a transformation script, data sources, and data targets. After the user has completed authoring the transformation, it can be initiated through job-based triggers, which can be scheduled or based on events.

#### File formats
AWS Glue supports two types of file formats:
1. Apache Parquet format is a type of file format that structures data in a columnar format, rather than a row-based format like a CSV or Microsoft Excel file. Apache Parquet format is optimal for analytical engines like Athena or Amazon Redshift Spectrum to query over.
2. AWS Glue now supports Apache Hudi, Apache Iceberg, and Delta Lake, which gives transactional capabilities to the data lake on Amazon S3.

#### Table
The metadata that represents user data is known as the table definition. Regardless of whether your data is stored in an Amazon S3 file, an Amazon RDS table, or elsewhere, a table defines the schema of that data. The table in the Data Catalog consists of information such as column names, data type definitions, partition details, and other metadata about the base dataset. The schema of your data is reflected in the AWS Glue table definition, while the actual data stays in its original data store (whether that be a file or a relational database table). The AWS Glue tables, which are cataloged in Data Catalog, can be used as sources or targets while creating an ETL job.

#### Transform
Transform is the code logic that is used to manipulate data into a different format and translate that into business logic.

#### AWS Glue triggers
A trigger, which initiates or starts an ETL job, can be defined based on a scheduled time or an event.
