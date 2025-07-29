# Databricks Computing: Complete Guide to Types and Settings
The scaling of compute and storage is the original benefits of distributed processing systems. Hadoop, Spark, and Databricks are all evolutions of this approach with further optimizations of both the compute and storage. Spark and Databricks have decoupled compute and storage to allow for better scaling of large data processing loads.

### Documentation
- [Databricks Compute Home Page](https://docs.databricks.com/aws/en/compute/)
  - [Databricks Compute Configurations](https://docs.databricks.com/aws/en/compute/configure)
  - [Databricks Compute Pools](https://docs.databricks.com/aws/en/compute/pools)
- [Chaos Genius Databricks Clusters 101](https://www.chaosgenius.io/blog/databricks-clusters/)
- [Claude Reasearch Resources](https://claude.ai/chat/4183081f-29d9-4ec3-9661-59d29dd00aaa)

## **Overview of Databricks Compute**

Databricks compute refers to the selection of computing resources available in the workspace that provide CPU, memory, storage and networking capacity for running data engineering, data science, and analytics workloads. The platform offers multiple compute types, each optimized for specific use cases and performance requirements.

## **Main Types of Databricks Compute**

### **1. Serverless Compute**

#### **Serverless Compute for Notebooks**
On-demand, scalable compute used to execute SQL and Python code in notebooks without provisioning clusters. This represents the newest evolution in Databricks computing.

**Key Features:**
- Instant startup and scaling
- Automatically managed by Databricks
- No cluster configuration required
- Versionless product with automatic upgrades

#### **Serverless Compute for Jobs**
On-demand, scalable compute used to run Lakeflow Jobs without configuring and deploying infrastructure.

**Settings and Configuration:**
- Performance optimized setting for faster startup and execution time
- Standard performance mode optimized for cost with slightly higher launch latency
- Outbound network policies for restricted domain access

### **2. All-Purpose Compute (Interactive Clusters)**

Provisioned compute used to analyze data in notebooks that can be created, terminated, and restarted using the UI, CLI, or REST API.

#### **Configuration Options:**

**Access Modes:**
- **Single User**: Only one user can access at a time
- **Shared**: Multiple users can collaborate simultaneously with session isolation

**Node Configuration:**
- Driver nodes maintain notebook state and run Apache Spark master, coordinating with Spark executors
- Worker nodes run Spark executors and handle distributed processing, with one executor per worker node

**Sizing Options:**
- **Single Node**: Intended for jobs using small amounts of data or non-distributed workloads
- **Multi-Node**: For larger distributed workloads

**Autoscaling Settings:**
- Optimized autoscaling scales up from min to max in 2 steps and can scale down by examining shuffle file state
- Standard autoscaling scales down exponentially starting with 1 node

### **3. Jobs Compute (Job Clusters)**

Provisioned compute used to run automated jobs, automatically created by the Databricks job scheduler and terminated when the job completes.

**Key Characteristics:**
- Ephemeral - created for specific jobs
- Cannot be restarted manually
- Cost-effective for batch workloads
- Optimized for automated ETL processes

### **4. SQL Warehouses**

SQL Warehouses come in three distinct types, each with different performance and cost characteristics:

#### **Serverless SQL Warehouses**

**Performance Features:**
- Rapid startup time (typically 2-6 seconds)
- Rapid upscaling for low latency and quick downscaling to minimize costs
- Intelligent Workload Management for optimal query demand handling

**Requirements:**
- Premium plan or above, specific regional support, and no external Hive metastore
- No public IP addresses and private connectivity between control and compute planes

#### **Pro SQL Warehouses**

**Features:**
- Support for Photon and Predictive IO but not Intelligent Workload Management
- Compute layer exists in your cloud account rather than Databricks account
- Startup time approximately 4 minutes with less responsive scaling

#### **Classic SQL Warehouses**

**Features:**
- Supports Photon but not Predictive IO or Intelligent Workload Management
- Entry-level performance with approximately 4-minute startup time
- Basic SQL query capabilities with manual resource management

### **5. Instance Pools**

Compute with idle, ready-to-use instances used to reduce start and autoscaling times.

#### **Pool Configuration Settings:**

**Capacity Management:**
- Minimum idle instances that don't terminate regardless of auto-termination settings
- Maximum capacity constraining all instances (idle + used)
- Idle instance auto-termination time before instances are returned to the cloud provider

**Performance Optimization:**
- Preloaded Databricks Runtime versions for faster cluster launches
- Autoscaling local storage with managed disks up to 5TB total per VM

**Cost Management:**
- Spot instance support for cost savings (worker nodes only)
- Best practice to set minimum idle instances to 0 to avoid paying for unused resources

## **Advanced Configuration Settings**

### **Runtime and Performance**

**Databricks Runtime:**
- Set of core components including Delta Lake, installed libraries, Ubuntu system, and GPU libraries
- Long Term Support (LTS) versions with three years of support

**Photon Acceleration:**
- Enabled by default on Databricks Runtime 9.1 LTS and above
- Vectorized query engine delivering up to 12x faster execution for SQL workloads

### **Security and Networking**

**Access Control:**
- Compute policies limiting configuration options for users without unrestricted cluster creation entitlements
- Personal Compute policy allowing single-machine compute resources by default

**Encryption:**
- Local disk encryption with unique keys per compute node for all data at rest

**Logging:**
- Cluster logs delivered every five minutes and archived hourly for driver node, worker nodes, and events

### **Instance Types and Sizing**

**Node Selection:**
- Different instance type families for memory-intensive vs compute-intensive workloads
- Balance between number of workers and instance size affects total executor cores and memory

**GPU Support:**
- GPU-accelerated clusters for computationally difficult tasks like deep learning
- Fleet instances don't support GPU instances

## **Best Practices and Recommendations**

### **Workload-Specific Configurations**

**Data Analytics:**
- Smaller number of larger nodes to reduce network and disk I/O for shuffle operations
- Storage optimized instances with disk cache enabled for repeated data access

**Machine Learning:**
- Single node compute with large node type for initial experimentation
- Avoid too many workers due to data shuffling overhead

**ETL Processing:**
- General-purpose instances supporting Photon for simple batch jobs
- Fewer workers for complex ETL requiring unions and joins to reduce data shuffling

### **Cost Optimization**

**Instance Pools:**
- Use spot instances for worker nodes and on-demand for driver nodes
- Set idle instance auto-termination to balance cost and availability

**Autoscaling:**
- Enable auto-termination and consider autoscaling based on typical workload patterns

This comprehensive overview shows how Databricks provides a sophisticated range of compute options, from fully managed serverless solutions to highly customizable traditional clusters, each with extensive configuration settings to optimize performance, cost, and security for specific use cases.
