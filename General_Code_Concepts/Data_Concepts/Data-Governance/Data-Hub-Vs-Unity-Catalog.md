# DataHub Vs Unity Catalog
They are actually quite different tools that often get compared but solve fundamentally different problems. Here's a breakdown:

- [DataHub](https://github.com/datahub-project/datahub)
- [Unity Catalog](https://unitycatalog.io/)

---

## What is DataHub Built On?

DataHub is **not** built on Unity Catalog. It's an original open-source project born at **LinkedIn** and is built on its own custom stack:

**Core infrastructure:**
- **Kafka** streams metadata change and audit events, updates usage metrics, and handles platform events.
- **MySQL** serves as the primary metadata store by default.
- **OpenSearch/Elasticsearch** powers search, lineage, glossary, and overall context discovery.
- **Neo4j** (optionally) handles graph queries for lineage relationships.
- The **GMS (Generalized Metadata Service)** is the heart of DataHub — a Java application that connects to the persistence layer and exposes a **GraphQL API**. It's the component around which all others revolve.

**Languages:** Java (38.7%), Python (35.5%), and TypeScript (24.2%).

**Metadata flow:** A MetadataChangeEvent (MCE) processor pulls Avro data, validates URNs, and sends to GMS, which persists to MySQL. GMS then publishes differences to a Kafka MetadataAuditEvent topic. The MAE processor picks those up and persists to Neo4j and Elasticsearch. The frontend queries GMS APIs.

---

## DataHub vs. Open Source Unity Catalog

They are **not related** — different origins, different purposes.

| Dimension | DataHub | OSS Unity Catalog |
|---|---|---|
| **Origin** | LinkedIn (2019), now independent | Databricks (donated to LF D&AI Foundation in 2024) |
| **Primary purpose** | Metadata platform / data catalog — discovery, governance, observability | Metastore — managing tables, volumes, and data assets in a lakehouse |
| **Focus** | Cross-platform metadata across your *entire* data stack | Primarily the Databricks/lakehouse ecosystem |
| **Connectors** | DataHub vastly outnumbers others in connectors, covering not just data and databases but also jobs, dashboards, dbt models, etc. | Narrower focus on data lake assets |
| **Lineage** | Deep, column-level lineage across many platforms | Basic; OSS Unity Catalog is still evolving and currently lacks advanced lineage tracking and discovery features |
| **Data model** | Functions as a "graph" representing not just data assets but also relationships between data-adjacent assets across the entire organization. You can even create logical concepts like Data Products or Domains that don't exist anywhere else. | Acts as an inventory/catalog of assets (tables, volumes) tied to a platform |
| **Table format support** | Supports all 3 major open table formats (Delta, Iceberg, Hudi) | Also supports all 3 major formats |
| **AI/unstructured data** | Unity Catalog and Gravitino have dedicated features focused on unstructured objects critical for AI scenarios; DataHub is more focused on structured metadata | Strong here |
| **License** | Apache 2.0 | Apache 2.0 |

---

## Where They Overlap

Both tools share some conceptual territory:

- **Metadata management** — both track what data assets exist and their properties
- **Governance** — both support access control and data classification
- **Open source** — both are Apache 2.0 licensed
- **Data lineage** — both offer some form of lineage tracking

## The Key Conceptual Difference

Think of it this way: Unity Catalog serves as an inventory of assets crucial to the Databricks ecosystem, like tables and volumes. DataHub serves a broader purpose — it functions not merely as a catalog but as a graph that represents not just data assets but also the relationships between data-adjacent assets that matter to the entire organization.

In short: **Unity Catalog is a metastore for a lakehouse**, while **DataHub is a metadata graph for your entire data stack** — including warehouses, BI tools, ML platforms, pipelines, and more. Many organizations actually use *both* — Unity Catalog to manage their lakehouse assets, and DataHub to provide cross-platform discovery and governance on top of it.
