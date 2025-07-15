# Lakeflow Jobs Overview
The portion of Lakeflow is responsible for the orchestration of you processing in Databricks. This is the same concept as Airflow, Step Functions, or Perfect. The system sets up DAGs for the automated data pipeline you want to run, then you set a trigger that would start the pipeline.

## Bolt-On Orchestration Tools
Databricks does support the use and execution from other orchestration tools like Airflow, Perfect, DBT, and Dagster. These tools can be combine together in Lakeflow Jobs as well, to create complex data pipelines.
<img width="1196" height="580" alt="image" src="https://github.com/user-attachments/assets/cae3af34-f75f-4b06-9226-69c7367ad94f" />

However you would need to setup them up within you cloud service with the correct configuration to run Databricks jobs. Additionally, there may not be as strong of an audit trail as the native Databricks Lakeflow Jobs. This makes it harder to track down issues, root out bad data, and understand reliability issues. 

## Lakeflow Jobs Structure
1. As stated Lakeflow jobs create DAGs for procesisng the data DAGs are simply the set of task you want to wire together and their dependencies.
  - They automatically detect jobs which can be run in parallel and does so.
2. Each task you must point to a compute/cluster. You can decide for each task to use the same or different compute.
3. Trigger the job to kick off according to your needs.
  - Scheduled
  - Continuous
  - File Arrival
  - Table Updates
  - Manual
4. Control Flow allows you to add in if-else conditions for running a branch or task.
5. Observability is baked in with logs and a UI for looking into past and present runs.

<img width="1231" height="517" alt="image" src="https://github.com/user-attachments/assets/5461a241-bf9d-46ef-938c-0640abb6d65b" />

## Building Blocks of Jobs
<img width="1299" height="558" alt="image" src="https://github.com/user-attachments/assets/fd8591db-274b-42c0-b90a-0476f5b9ed93" />

### Types of Jobs
<img width="1210" height="533" alt="image" src="https://github.com/user-attachments/assets/da48886d-f800-4c64-addf-0cc031b7a528" />

### Options
Depending on the type of Task the configurations may vary. 
- Defining paths to code
- adding libraries
- parameterizing variables
- enabling notification
- Compute option
- and more depending


## CLuster Types
Interactive Clusters:
- Purpose: an all purpose cluster which can be shared by multiple users.
- Use Case: this is best for adhoc analysis and exploration, because its can be used across many workload types.
- This type of cluster is less cost efficient. Also, you have to manually manage (start/stop) the cluster.

Job Clusters:
- Purpose: a production grade compute which will start and stop with the Job in Lakeflow.
- Use Case: Production Lakeflow Jobs.
- The type of cluster is 50% because of the efficent start and stop mechanism.
- You can reuse this cluster across tasks for better price performance. Over use across too many task can hurt runtime however.

Serverless
- Purpose: a fully managed service that is operationally simpler and more reliable.
- They provide a faster cluster and auto-scaling capabilityes providing a better experience for a lower cost.
- Out of the boc optimizations to provide a lower overall TCO.

SQL Warehouse
- Purpose: The warehouse is specifically optimized for SQL workloads.
- Use Case: Either production SQL processing or Adhoc SQL-only work.

### More Cluster Details:
I'll search for the latest information about Databricks Serverless compute compared to Job Clusters to give you accurate details on cost and performance differences.Let me get more detailed information about the cost comparison between Databricks Serverless and Job Clusters.Based on my research, here's a comprehensive comparison of Databricks Serverless compute units versus Job Clusters in terms of cost and performance:

## Cost Comparison
**Serverless is NOT necessarily cheaper than optimized Job Clusters.** An optimized cluster by Gradient outperformed Databricks serverless jobs by roughly 60% from a cost perspective in testing by Sync Computing. However, the cost picture is nuanced:

**When Serverless costs more:**
- For long-running workloads (1+ hours), optimized Job Clusters often provide better cost efficiency
- Serverless was able to run the job much faster, taking only 30 minutes which was great to see. Unfortunately, the runtime savings didn't translate to the cost savings
- You lose cloud provider discounts since on serverless the compute runs inside the Databricks environment

**When Serverless can be cost-effective:**
- A great use case for serverless, which we fully endorse, is using serverless for short (<5 min) jobs. The elimination of spin up time for your cluster is a massive win
- Efficiency improvements that result in a greater than 25% reduction in existing and future, serverless compute costs for most customers, especially those with short-duration workloads
- You get a 50% price reduction on serverless compute for Workflows and DLT and a 30% price reduction for Notebooks (promotional pricing through January 2025)

## Performance Comparison

**Startup Time:** Serverless has a significant advantage
- Unlike traditional clusters that take minutes to start, Serverless SQL Warehouses are ready in just 3 seconds
- We saw roughly 80% reduction in runtime! This improvement is mostly due to the complete elimination of cluster spin up time which can take 5-10 minutes

**Runtime Performance:** Mixed results
- Overall, DBSQL and Jobs Serverless were about the same in terms of runtime
- Serverless can run some jobs faster due to automatic optimization
- However, The big downside of jobs serverless is that there's no way to tune the cluster to adjust cost or runtime. You basically have to live with whatever Databricks decides

## Key Trade-offs

**Serverless Advantages:**
- **Zero configuration:** Something quite unique about Databrick jobs serverless is that there are zero knobs
- **Instant startup:** Eliminates 5-10 minute cluster initialization
- **Automatic scaling and optimization:** Serverless includes a new autoscaler which is smarter and more responsive to your workload's needs than the autoscaler in classic compute
- **Automatic updates:** Always runs latest Databricks Runtime versions

**Job Cluster Advantages:**
- **Cost optimization potential:** Can be 60% cheaper when properly tuned
- **Full control:** Configure instance types, cluster size, Spark settings
- **Flexibility:** Support for spot instances and custom configurations
- **Predictable pricing:** You know exactly what you're paying for

## Recommendations

**Use Serverless when:**
- Running short-duration jobs (<5 minutes)
- Need fast startup times for ad-hoc analysis
- Want zero infrastructure management
- Team lacks Spark optimization expertise

**Use Job Clusters when:**
- Running long-duration, predictable workloads
- Cost optimization is critical
- Need specific instance types or configurations
- Have existing cloud provider discounts
- Require features not supported in Serverless

The bottom line: Serverless prioritizes convenience and fast startup over cost optimization, while Job Clusters offer maximum flexibility and potential cost savings but require more expertise to optimize properly.
