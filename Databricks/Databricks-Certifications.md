# Databricks Certifications
At the time of making this page Databricks did not have the free classes they offer well organized into groups for the certifications they offer. To avoid the fee of the expert led classes I have the videos organized below. These classes are helpful, but the more background in Spark, SQL, and Data Engineering the easier studying for these exams will be. 
<br>**Recertification:** Recertification is required every two years to maintain your certified status

Related Certifications:
- [AWS Cloud Certs. for Data Engineers](https://github.com/ajlinhard/byte-size-docs/blob/main/AWS/AWS-Certifications.md)
- [Snowflake Certs.](https://github.com/ajlinhard/byte-size-docs/blob/main/Snowflake/Snowflake-Certifications.md)
- [Databricks All Certs.](https://www.databricks.com/learn/training/home)

## Table of Contents:
- [Apache Spark Course](https://www.databricks.com/training/catalog?roles=apache-spark-developer)
- [Summary and Recommendations](#Summary-and-Recommendations)
- [Databricks Certified Data Engineer Associate](#Databricks-Certified-Data-Engineer-Associate)
- [Databricks Certified Data Engineer Professional](#Databricks-Certified-Data-Engineer-Professional)
- [Complete Certification Course List](https://community.databricks.com/t5/events/virtual-learning-festival-9-april-30-april/ev-p/111620)

---
## **Summary and Recommendations**

**For Beginners:**
- Start with **Databricks Associate** (6+ months experience) or **SnowPro Core** 
- AWS requires more experience (2-3 years) for their Data Engineer certification

**For Experienced Engineers:**
- **Databricks Professional** for advanced lakehouse architecture
- **Snowflake Advanced Data Engineer** for cloud data warehousing expertise
- **AWS Data Engineer Associate** for comprehensive cloud data engineering skills

Each certification focuses on different aspects of the modern data stack, with Databricks emphasizing lakehouse architecture and ML integration, Snowflake focusing on cloud data warehousing and sharing, and AWS covering the full spectrum of cloud-native data engineering services.

---
## **Databricks Certified Data Engineer Associate**
---

This certification assesses the ability to use the Databricks Lakehouse Platform to complete introductory data engineering tasks, including understanding the platform's workspace, architecture, and capabilities. It evaluates skills in performing multi-hop architecture ETL tasks using Apache Spark SQL and Python in both batch and incrementally processed paradigms.
<br>**[PDF of Certification Details](https://github.com/ajlinhard/byte-size-docs/blob/main/Databricks/docs/databricks-certified-data-engineer-associate-exam-guide-1-mar-2025.pdf)**

**Topics & Tools Covered:**
- **Core Platform Knowledge:** Understanding of the Lakehouse Platform and its workspace, its architecture, and its capabilities
- **Data Processing:** Apache Spark SQL and Python for ETL pipelines
- **Delta Lake:** Table management, manipulation, and optimizations
- **Multi-hop Architecture:** Building production-ready ETL pipelines
- **Databricks SQL:** Queries and dashboards in production
- **Security:** Entity permissions and access control

**Prerequisites:** 6+ months of hands-on experience performing the data engineering tasks outlined in the exam guide

### Courses:
- [Data Ingestion with Delta Lake](https://customer-academy.databricks.com/learn/courses/2963/data-ingestion-with-delta-lake/lessons)
- [Deploy Workloads with Databricks Workflows](https://customer-academy.databricks.com/learn/courses/1365/deploy-workloads-with-databricks-workflows)
- [Build Data Pipelines with Delta Live Tables](https://customer-academy.databricks.com/learn/courses/2971/build-data-pipelines-with-delta-live-tables/lessons)
- [Data Management and Governance with Unity Catalog](https://customer-academy.databricks.com/learn/courses/3144/data-management-and-governance-with-unity-catalog)

### What you should Know!
- Data Ingestion with Lakeflow Connect
  - Describe Lakeflow Connect as a solution for simple and scalable data ingestion
  - Understand how Unity Catalog structures storage of data objects
  - Explain the benefits of Delta tables and the Medallion architecture.
  - Describe how to ingest files from cloud object storage as Delta tables using CREATE TABLE AS and COPY INTO, while adding input file metadata in Bronze layer tables.
  - Explain how to leverage rescued columns for data ingestion
  - Explain how to ingest and flatten semistructured data like XML and JSON files from cloud storage
  - Describe the options available to ingest data from existing enterprise systems into Databricks
  - Describe how MERGE INTO can be utilized during ingestion
  - Understand how Auto Loader and other SQL TVFs can be used for ingestion
- Workflows
  - Understand the role of Lakeflow Jobs within the Databricks ecosystem as a unified orchestration platform for data, analytics, and AI workloads.
  - Design and implement data workloads using Directed Acyclic Graphs (DAGs), demonstrating the relationship between jobs, tasks, and dependencies.
  - Configure various job scheduling options including manual, scheduled, file arrival, and continuous triggers to automate workflow execution.
  - Implement advanced workflow features such as conditional task execution, run-if dependencies, and repair runs to create robust, fault-tolerant data pipelines.
  - Apply best practices for production workloads including selecting appropriate compute options, implementing modular orchestration, and utilizing proper error handling techniques.
- Build Data Pipelines with Lakeflow Declarative Pipelines
  - Understand the core concepts and components of Lakeflow Declarative Pipelines, including the function and differences between streaming tables, materialized views, and temporary views.
  - Identify and configure Lakeflow pipeline settings, such as compute, data assets, trigger modes, and advanced options.
  - Develop a functional Lakeflow Declarative Pipeline using the new pipeline editor and SQL-based syntax.
  - Incorporate data quality expectations into a Lakeflow pipeline to validate and enforce data integrity.
  - Analyze event logs and pipeline metrics to understand the full execution and lifecycle of a Lakeflow Declarative Pipeline.
  - Design and implement a Change Data Capture (CDC) to a pipeline using APPLY CHANGES INTO to handle slowly changing dimensions (SCD).
- Data Management and Governance with Unity Catalog
  - Explain the importance of data governance and challenges in traditional data lake environments.
  - Differentiate between managed and external tables, and evaluate the architecture of Unity Catalog.
  - Utilize SQL commands to navigate and inspect metastore components, and assess data segregation strategies.
  - Identify query lifecycle steps and Databricks roles for effective data governance and security within Unity Catalog.
  - Implement privilege assignments and fine-grained access control strategies using SQL syntax and dynamic views in Databricks.
  - Assess the effectiveness and implications of different privilege scenarios, inheritance models, and access control mechanisms in Unity Catalog.

---
## **Databricks Certified Data Engineer Professional**
---
This certification assesses an individual's ability to use Databricks to perform advanced data engineering tasks, including understanding of the Databricks platform and developer tools like Apache Spark, Delta Lake, MLflow, and the Databricks CLI and REST API.
<br>**[PDF of Certification Details](https://github.com/ajlinhard/byte-size-docs/blob/main/Databricks/docs/databricks-certified-data-engineer-professional-exam-guide-1-mar-2025.pdf)**

**Topics & Tools Covered:**
- **Advanced Platform Tools:** Apache Spark™, Delta Lake, MLflow, and the Databricks CLI and REST API
- **Pipeline Optimization:** Building optimized and cleaned ETL pipelines
- **Data Modeling:** Ability to model data into a lakehouse using knowledge of general data modeling concepts
- **Production Best Practices:** Ensuring that data pipelines are secure, reliable, monitored and tested before deployment
- **Programming Languages:** Code examples in this exam will primarily be in Python. However, any and all references to Delta Lake functionality will be made in SQL

**Prerequisites:** 1+ years of hands-on experience performing the data engineering tasks outlined in the exam guide

### Courses:
- [Databricks Streaming and Delta Live Tables - Delta Dawn](https://www.databricks.com/training/catalog/databricks-streaming-and-delta-live-tables-2972)
- [Databricks Data Privacy](https://customer-academy.databricks.com/learn/courses/3767/databricks-data-privacy)
- [Databricks Performance Optimization Delta Dawn](https://customer-academy.databricks.com/learn/courses/2967/databricks-performance-optimization/lessons)
- [Automated Testing and Deployment with Databricks Asset Bundle](https://customer-academy.databricks.com/learn/courses/3489/automated-deployment-with-databricks-asset-bundles)
<br>Not Officially Recommended
- [Building Data Pipelines with Delta Live Tables](https://customer-academy.databricks.com/learn/courses/2971/build-data-pipelines-with-delta-live-tables/lessons)
- [DevOps Essentials for Data Engineers](https://www.databricks.com/training/catalog/devops-essentials-for-data-engineering-3640)

### Extra Courses:
- [Data Ingestion with Delta Lake](https://customer-academy.databricks.com/learn/courses/2963/data-ingestion-with-delta-lake/lessons/)
- [Data Preparations for Machnine Learning](https://customer-academy.databricks.com/learn/courses/2343/data-preparation-for-machine-learning)
- [Advance Machine Learning Operations](https://customer-academy.databricks.com/learn/courses/3508/advanced-machine-learning-operations)
- [Create Your First Databrick Express Workspace](https://customer-academy.databricks.com/learn/courses/3697/create-your-first-workspace-using-databricks-express)
- [Automate Production Workdlows](https://customer-academy.databricks.com/learn/courses/2143/automate-production-workflows)
- [AWS Platform Architect - Learning Plan](https://customer-academy.databricks.com/learn/learning-plans/262/aws-databricks-platform-architect-learning-plan-public)


