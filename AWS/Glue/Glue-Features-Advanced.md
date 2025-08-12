# AWD Glue Advanced Features
AWS Glue is a scalable data integration service that streamlines the ETL process using built-in connectors. You can design complex workflows using crawlers, jobs, and initiations, and choose to author the jobs using code or visual transformations. The jobs can be deployed using AWS CloudFormation, which acts as infrastructure as code in JSON or YAML, and can be version-controlled in Bitbucket or GitHub. AWS Glue also offers centralized monitoring through a single pane of glass. This helps you check the status of your ETL pipeline and start, stop, and rerun jobs they have created. 

### Documentation
- [AWS Glue Features](https://aws.amazon.com/glue/features/)

## Partitioning
Partitioning is a technique that organizes related data together to minimize the amount of data scanned, thus improving query speed. One example is a sales database that is divided into partitions based on year, month, and day. To view sales from a specific day (for example, January 1, 2022), include a filter condition with the date, month, or year when writing scan queries. This way, you can limit the data scan for a particular year or month of data.



./Sales S3 Bucket

|--- Sales

    |--- Year=2022

        |--- Month=January

            |--- Day=1

            |--- Day=2 

            |--- Day=3

        |--- Month=February

    |--- Year=2021

 

By partitioning data in the Amazon S3 data lake, AWS Glue can scan only the data that matches the transformation logic. The AWS Glue crawler or jobs determine which data to process based on the underlying schema and partitioning strategy. If there are no new partitions, then there is no need to run the AWS Glue crawler. But if the schema has partitions that are added hourly or daily, the crawler will run with the schedule to keep the Data Catalog up to date with new data. To maximize performance and minimize cost, scan only the necessary data. This can be accomplished by implementing a targeted partitioning strategy focusing on specific columns or partitions.


## Run locally first
Experienced developers believe developing and testing ETL code for their business logic locally is fast and cost-effective, even in present time. AWS Glue provides options for local development through a Docker image and the AWS Glue Studio ETL libraries. Additionally, users can test their scripts remotely using AWS Glue interactive sessions in AWS Glue Studio.


## Using Auto Scaling for AWS Glue
With the AWS Glue Auto Scaling feature, ETL jobs can dynamically adjust the number of workers based on the processing demand for complex transformations. When the demand decreases, the number of workers returns to its original state. By doing this, developers don’t have to hardcode workers needed for their jobs. This feature is available in AWS Glue version 3.0 or higher.

With Auto Scaling activated, AWS Glue can do the following: 

AWS Glue will automatically add and remove workers from the cluster, based on the parallelism of each stage or micro-batch of the job run.
This eliminates the need to experiment manually with different worker configurations, with AWS Glue selecting optimal resources for your workload.
You can monitor the cluster size during the job run by viewing CloudWatch metrics on the job run details page in AWS Glue Studio.
For more information about AWS Glue Auto Scaling, see [Using Auto Scaling for AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/auto-scaling.html).


## Compression and file format
Compressing your data conserves storage space and enhances the performance of distributed processing by minimizing network traffic between Amazon S3, AWS Glue, and other AWS services. Choosing a file format that supports compression, such as the columnar Parquet format, can improve performance. It is usually more efficient to work with fewer larger files, rather than multiple smaller files, when querying data stored in Amazon S3. By properly partitioning, compressing, and formatting your data, you can maximize the capabilities of query engines like Amazon Athena and Amazon Redshift Spectrum. This can help lead to faster query performance and reduced costs.


## Use job bookmarks: Incremental processing
AWS Glue has a mechanism for tracking the records processed in each job, known as job bookmarks. These bookmarks persist state information from previous job runs and help prevent reprocessing of old data. Using job bookmarks, developers can efficiently process only new or incremental files when rerunning a job. This provides efficient maintenance of state information and optimized processing.


## Security and encryption of data
Data protection is a key factor to consider when implementing real-world projects. To ensure the security of your data, AWS Glue offers various encryption options, including encryption at rest and in motion. When using AWS Glue to author jobs and develop scripts, your data can be encrypted at rest. Additionally, metadata stored in the Data Catalog can be encrypted using keys from the AWS Key Management Service (AWS KMS). SSL encryption is also available for data in motion through AWS Glue, and you can configure encryption settings for crawlers, ETL jobs, and development endpoints.


## Job monitoring
Monitoring production in AWS Glue jobs is an important part of maintaining the reliability, availability, and performance of AWS Glue. You can use the following automated monitoring tools to watch AWS Glue. Further details can be found in the resources section. 

Amazon EventBridge
Amazon CloudWatch Logs
AWS CloudTrail

## Amazon Q Developer
AWS Glue can be integrated with Amazon Q Developer, a coding companion. With this integration, you can develop code quickly and conveniently, which can help speed up your data preparation for analytics and ML. When you use AWS Glue Studio notebooks to write code in Python, or even just type in English, Amazon Q Developer provides you with real-time recommendations. You can then either accept the top suggestion, view more suggestions, or continue writing your own code.


For more information on using Amazon Q Developer with AWS Glue, see [Amazon Q data integration in AWS Glue](https://aws.amazon.com/blogs/big-data/build-data-integration-jobs-with-ai-companion-on-aws-glue-studio-notebook-powered-by-amazon-codewhisperer/).


## Transactional data lake
AWS Glue for Apache Spark now supports three open-source data lake storage frameworks: Apache Hudi, Apache Iceberg, and Linux Foundation Delta Lake. These frameworks provide consistent reading and writing of data in Amazon S3. They streamline incremental data processing in data lakes built on Amazon S3. This removes the need for a separate connector and reduces configuration steps in AWS Glue for Apache Spark jobs. With these frameworks, you can do time-travel queries; atomicity, consistency, isolation, and durability (ACID) transactions; streaming ingestion; change data capture; upserts; and deletes.


For more information, see [Using Data Lake Frameworks with AWS Glue ETL Jobs](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-datalake-native-frameworks.html).
