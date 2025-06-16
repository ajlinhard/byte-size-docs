
# Databricks Runtime vs. Apache Ecosystem
The Databirkcs platform and the backend engine of the system the Databricks Runtime has its origins in the Apache ecosystem: Hadoop, Spark, Hive, etc. However, most of these [Apache Data tools](https://github.com/ajlinhard/byte-size-docs/blob/main/Architectures-Tools/Data/Apache-Data-Tools-Overview.md) are **not** integrated into the Databricks Runtime, as Databricks has built its own unified analytics platform that replaces many of these traditional Hadoop ecosystem components with its own optimized implementations.

## What's NOT in Databricks Runtime

**Hadoop Ecosystem Tools**: Databricks doesn't include Hadoop, HBase, HCatalog, Hive (traditional), Pig, Oozie, or Hue. Databricks was designed to move beyond the Hadoop ecosystem's complexity by providing a cloud-native alternative that eliminates the need for these separate tools.

**Query Engines**: Presto/Trino and Phoenix are not included since Databricks provides its own SQL engine and Delta Lake for storage optimization.

**Workflow Tools**: Oozie is replaced by Databricks Workflows (formerly Jobs), and Livy is unnecessary since Databricks provides direct Spark cluster access through notebooks.

## What IS in Databricks Runtime

**Apache Spark**: This is the core compute engine, but Databricks provides an optimized version with performance improvements like Photon (their vectorized query engine) and runtime optimizations not available in open-source Spark.

**TensorFlow**: Fully supported along with other ML frameworks like PyTorch, scikit-learn, and MLflow for the complete machine learning lifecycle.

**JupyterHub/Notebook Functionality**: Databricks provides its own collaborative notebook environment that's similar to JupyterHub but with deeper integration into the Spark ecosystem and better collaboration features.

**Tez**: Not directly included, but Databricks' optimized Spark SQL engine provides similar query optimization capabilities.

## Databricks' Replacement Strategy

**Instead of Hive**: Databricks provides Spark SQL with Delta Lake, which offers ACID transactions, schema evolution, and better performance than traditional Hive. You can still read Hive metastore tables, but most organizations migrate to Delta Lake format.

**Instead of HBase**: Databricks uses Delta Lake for both batch and streaming workloads, though it lacks HBase's millisecond point-lookup capabilities. For real-time serving, organizations typically use external key-value stores integrated through Databricks' streaming capabilities.

**Instead of Presto**: Databricks SQL (formerly SQL Analytics) provides fast interactive queries with better integration into the Databricks ecosystem and superior performance optimization through Photon.

**Instead of Workflow Tools**: Databricks Workflows handles job orchestration, dependency management, and scheduling without needing separate tools like Oozie.

## Integration Patterns in Healthcare

**Migration Path**: Healthcare organizations typically migrate from traditional Hadoop clusters to Databricks by:
- Converting Hive tables to Delta Lake format
- Replacing Oozie workflows with Databricks Workflows  
- Moving from separate Presto/HBase systems to unified Spark+Delta Lake architecture
- Migrating TensorFlow models to Databricks' MLflow model registry

**Hybrid Architectures**: Some healthcare organizations maintain hybrid setups where legacy HBase systems handle real-time patient lookups while Databricks processes analytical workloads, connected through streaming integrations.

**External Integrations**: While these tools aren't in Databricks Runtime, you can integrate with external systems running them:
- Read from HBase using Spark connectors
- Query external Presto/Trino clusters through JDBC
- Ingest data from Hadoop clusters using Spark's built-in connectors

## Why Databricks Made These Choices

**Simplification**: Rather than managing 10+ different tools, Databricks provides a unified platform where Spark handles most use cases with Delta Lake providing the storage layer.

**Performance**: Databricks' optimized Spark runtime with Photon often outperforms the combination of separate Hadoop ecosystem tools.

**Cloud-Native**: These traditional tools were designed for on-premises clusters, while Databricks is built for cloud-first architectures with auto-scaling and managed infrastructure.

**Developer Experience**: Instead of learning multiple query languages (HiveQL, Pig Latin, Phoenix SQL), developers work with standard Spark SQL and Python/Scala APIs.

## Practical Implications for Healthcare

Healthcare organizations moving to Databricks typically see simplified architectures but may need to address specific gaps:

- **Real-time lookups**: External caching layers or purpose-built serving systems for patient data requiring millisecond response times
- **Fine-grained security**: Delta Lake's table-level security may require additional tooling for cell-level access control previously handled by HBase
- **Legacy integration**: Custom connectors or data pipelines to integrate with existing Hadoop ecosystem deployments that can't be immediately migrated

The trade-off is architectural simplicity and better performance for most analytics workloads, but potential gaps in specialized operational use cases that some of these traditional tools handled better.
