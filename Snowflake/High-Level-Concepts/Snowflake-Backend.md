# Snowflake Backend
Snowflake's backend system is not built on top of Spark or Hadoop. The Snowflake data platform is not built on any existing database technology or "big data" software platforms. Instead, Snowflake combines a completely new SQL query engine with an innovative architecture natively designed for the cloud.

## **Snowflake's Processing Engine: Virtual Warehouses**

Snowflake processes queries using "virtual warehouses". Each virtual warehouse is an MPP compute cluster composed of multiple compute nodes allocated by Snowflake from a cloud provider. Each virtual warehouse is an independent compute cluster that does not share compute resources with other virtual warehouses.

### **What Virtual Warehouses Are:**

Virtual Warehouses are the primary compute primitive in Snowflake and are Massively Parallel Processing (MPP) compute clusters composed of multiple Virtual Machines (VMs) provisioned by Snowflake and run software managed by Snowflake.

A warehouse provides the required resources, such as CPU, memory, and temporary storage, to perform the following operations in a Snowflake session: Executing SQL SELECT statements that require compute resources (e.g. retrieving rows from tables and views).

### **How Virtual Warehouses Work:**

**Scaling and Sizing:**
- An XSMALL virtual warehouse consists of 8 CPUs, and a critical aspect of Snowflake is that any given warehouse can execute multiple queries in parallel. Equally, a single query can (if sensible) execute queries in parallel using all eight CPUs to maximize performance.
- Virtual warehouses come in different sizes from XSmall to 6XLarge, with each size doubling the compute resources
- With multi-cluster warehouses, Snowflake supports allocating, either statically or dynamically, additional clusters to make a larger pool of compute resources available.

**Dynamic Management:**
- Warehouses can be started and stopped at any time. They can also be resized at any time, even while running, to accommodate the need for more or less compute resources, based on the type of operations being performed by the warehouse
- Auto-suspend and auto-resume capabilities minimize costs by shutting down when not in use

## **Snowflake's Unique SQL Query Engine**

The Snowflake data platform is not built on any existing database technology or "big data" software platforms such as Hadoop. Instead, Snowflake combines a completely new SQL query engine with an innovative architecture natively designed for the cloud.

### **Query Processing Architecture:**

The SQL query execution is handled by Snowflake's Query Processing Layer, which dynamically optimizes and parallelizes queries over several compute clusters. It ensures great performance and scalability by decoupling computation and storage, allowing for on-demand resource allocation based on query complexity and workload.

**Key Processing Features:**
- **Automatic Query Optimization:** Snowflake's Query Processing Layer optimizes SQL queries automatically, modifying execution plans based on underlying data distribution and query complexity to ensure efficient processing.
- **Parallel Execution:** Query execution is performed in parallel across many compute clusters, leveraging Snowflake's multi-cluster architecture to achieve high concurrency and faster results for complex analytical workloads.

## **Data Storage and Management**

### **Micro-Partitions Storage System:**

All data in Snowflake tables is automatically divided into micro-partitions, which are contiguous units of storage. Each micro-partition contains between 50 MB and 500 MB of uncompressed data (note that the actual size in Snowflake is smaller because data is always stored compressed). Groups of rows in tables are mapped into individual micro-partitions, organized in a columnar fashion.

### **Columnar Storage Format:**

Columns are stored independently within micro-partitions, often referred to as columnar storage. This enables efficient scanning of individual columns; only the columns referenced by a query are scanned. Columns are also compressed individually within micro-partitions. When data is loaded into Snowflake, Snowflake reorganizes that data into its internal optimized, compressed, columnar format.

### **Data Management Features:**

**Automatic Optimization:**
- Once data is loaded into Snowflake, it utilizes its internal optimization and compression techniques to store the data into central repository as columnar format. Snowflake owns responsibilities to all aspects of data management like how data is stored using automatic clustering of data, organization and structure of data, compression technique by keeping data into many micro-partitions, metadata, statistics and many more.

**Intelligent Query Pruning:**
- The micro-partition metadata maintained by Snowflake enables precise pruning of columns in micro-partitions at query run-time, including columns containing semi-structured data. In other words, a query that specifies a filter predicate on a range of values that accesses 10% of the values in the range should ideally only scan 10% of the micro-partitions.

## **Three-Layer Architecture**

Snowflake's backend operates on a unique three-layer architecture:

1. **Storage Layer:** Snowflake stores this optimized data in cloud storage. Snowflake manages all aspects of how this data is stored — the organization, file size, structure, compression, metadata, statistics, and other aspects of data storage are handled by Snowflake.

2. **Compute Layer:** Virtual warehouses that process queries independently without sharing resources

3. **Cloud Services Layer:** The cloud services layer is a collection of services that coordinate activities across Snowflake. These services tie together all of the different components of Snowflake in order to process user requests, from login to query dispatch.

## **Performance Optimization**

The processing engine includes several built-in optimization features:

- **Caching:** Multiple layers including result cache, local disk cache, and remote disk cache
- **Dynamic Query Optimization:** Real-time adjustments during query execution
- **Automatic Clustering:** Organizes data for optimal query performance
- **Vectorized Processing:** Optimized for columnar data operations

This architecture enables Snowflake to deliver high performance, automatic scaling, and efficient resource utilization while abstracting away the complexity of infrastructure management from users.
