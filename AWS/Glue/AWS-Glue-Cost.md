# AWS Glue Cost
The cost amounts of most AWS services are always adjusting. So reviewing the official documentation is always a good idea. The main cost for Glue is your S3 storage and DPUs (Data Processing Units). While there are other charges they are charges this is where the bulk of the cost is, especially once in production.

### Documentation
- [AWS Glue Pricing](https://aws.amazon.com/glue/pricing/)
- [AWS Glue Pricing Calculator](https://calculator.aws/#/createCalculator/Glue)

# The Cost
AWS Glue consists of various components. Each of these has a specific purpose and cost structure. Please note pricing can vary by AWS Region and can change. The following information is as of Q3 2023. 

### AWS Glue ETL jobs and interactive sessions
With AWS Glue, there are no upfront fees or costs for maintaining infrastructure and no charges for starting up or shutting down. Users only pay for what they use, which means charges are only applied to job runs. The cost is based on an hourly rate that is rounded to the nearest second, calculated based on the number of DPUs used to run your ETL job. AWS Glue offers different worker types with varying capacities, including Standard, G.1X, G.2X, and G.025X. One DPU is equivalent to 4 vCPUs and 16 GB of memory.

Users can use AWS Glue interactive sessions for interactive ETL code development, but they will only incur charges if they decide to run some transformations as a job. The duration of the session determines the cost of interactive sessions and the amount of DPUs used. Interactive sessions can be set with adjustable idle timeouts, and are billed a minimum of 1 minute. Interactive sessions require a minimum of 2 DPUs, with a default of 5 DPUs.

AWS Glue Studio allows data previews to test your transformations during the job authoring process. Each AWS Glue Studio data preview session uses 2 DPUs, runs for 30 minutes, and stops automatically.

### Data Catalog and storage requests
With Data Catalog, you have a free tier to store a certain number of metadata objects such as tables, table versions, partitions, and databases. If you exceed this limit, you will incur charges based on the number of additional objects you store over the free tier. The pricing is applied on a per-object basis and is based on the number of objects exceeding the free-tier limit. It's important to note that the charges apply only to the Data Catalog and not to any other AWS services that you may use with it.

### AWS Glue crawlers
AWS Glue crawlers incur an hourly charge for discovering data and updating the Data Catalog based on the number of DPUs used. The crawler is billed in 1-second increments, with a minimum of 10 minutes for each crawl, and rounded up to the nearest second. Using AWS Glue crawlers is optional, and users can populate the Data Catalog directly through the API.

### DataBrew interactive sessions
DataBrew charges users for authoring on a per-session basis. A session is initiated when a DataBrew project is opened and users are billed for the total number of sessions used. Each session can last for 30 minutes and is billed in 30-minute increments. First-time users of DataBrew are offered the first 40 interactive sessions for free.

### DataBrew jobs
Users are charged an hourly rate based on the number of DataBrew workers used to run the job. By default, DataBrew allocates five workers to each job. There is a 1-minute billing duration for each job. 

### AWS Glue Flex execution
AWS Glue has introduced a new option that can help customers reduce the costs of their pre-production, testing, and non-critical data integration workloads by as much as 34 percent. This option is known as AWS Glue Flex execution, which utilizes spare capacity in AWS to run AWS Glue jobs.

For more information, see [Introducing AWS Glue Flex Jobs](https://aws.amazon.com/blogs/big-data/introducing-aws-glue-flex-jobs-cost-savings-on-etl-workloads/).

### AWS Glue Data Quality
With AWS Glue Data Quality, users can standardize their data by comparing it with the source system and preserving the approved data for downstream use. AWS Glue automatically generates rule recommendations based on computed statistics of the data and uses these statistics to verify its accuracy. Additionally, custom rules can be created by writing logic using the straightforward Data Quality definition language. More info at [AWS Glue Data Quality](https://docs.aws.amazon.com/glue/latest/dg/glue-data-quality.html)

### AWS Glue Schema Registry
A schema defines the structure and format of a data record. With AWS Glue Schema Registry, you can manage and enforce schemas on your data streaming applications using convenient integrations. These integrations include Apache Kafka, Amazon Managed Streaming for Apache Kafka, Amazon Kinesis Data Streams, Amazon Kinesis Data Analytics for Apache Flink, and AWS Lambda.

## What are DPUs?
DPUs (Data Processing Units) are the compute capacity units that AWS Glue uses to measure and bill for processing power in Glue jobs.

**What DPUs represent:**
- Each DPU provides 4 vCPUs and 16 GB of memory
- They determine how much compute resources are allocated to your Glue job
- You can configure the number of DPUs when creating or running a job

**Key characteristics:**
- **Minimum allocation:** Most Glue job types require a minimum of 2 DPUs
- **Scaling:** You can allocate anywhere from 2 to 100 DPUs (or more with service limit increases)
- **Billing:** You're charged based on DPU-hours (number of DPUs × time running)
- **Granularity:** Billed per second with a 1-minute minimum

**Job type considerations:**
- **Glue ETL jobs:** Default is usually 10 DPUs, can be adjusted based on data volume and complexity
- **Glue Streaming jobs:** Minimum 2 DPUs
- **Ray jobs:** Different DPU configurations available
- **Python Shell jobs:** Use a fraction of a DPU (0.0625 or 1 DPU options)

**Performance impact:**
- More DPUs = more parallelism and faster processing
- But there's a point of diminishing returns - adding more DPUs won't help if your job isn't designed to scale horizontally
- The optimal number depends on your data size, transformation complexity, and I/O patterns

**Cost optimization tip:** Start with the default DPU allocation, monitor job performance, then adjust up or down based on whether you need faster processing or want to reduce costs.

### The 1-minute Minimum Explained
The 1-minute minimum is **per job run**, not per billing cycle.

Here's how it works:

**Per job run:**
- Each time you start a Glue job, you're charged for a minimum of 1 minute, even if the job completes in 30 seconds
- If your job runs for 2 minutes and 15 seconds, you're charged for exactly 2 minutes and 15 seconds (rounded to the nearest second)
- If you run the same job 10 times in a day, and each run takes 30 seconds, you'd be billed for 10 minutes total (1 minute × 10 runs)

**Example scenarios:**
- Job runs for 45 seconds → billed for 1 minute
- Job runs for 1 minute 30 seconds → billed for 1 minute 30 seconds  
- Job runs for 3 minutes 47 seconds → billed for 3 minutes 47 seconds

This per-job minimum can add up if you have many short-running jobs. For cost optimization with frequently executed short jobs, consider:
- Batching multiple small transformations into a single job
- Using Glue workflows to chain related jobs efficiently
- For very lightweight tasks, consider Python Shell jobs which use fractional DPUs

The billing is calculated as: (Number of DPUs) × (Runtime in seconds, minimum 60) × (DPU hourly rate ÷ 3600)
