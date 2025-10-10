# Relational vs Multi-Dimensional Databases
A **relational database** and a **multi-dimensional database** are designed for different purposes and organize data in fundamentally different ways:

## Relational Database (RDBMS)

- **Structure**: Data is organized in tables (rows and columns) with relationships between tables defined through keys
- **Model**: Based on relational theory - think of it like spreadsheets linked together
- **Queries**: Uses SQL for querying and manipulating data
- **Optimized for**: Transaction processing (OLTP) - handling lots of individual records like customer orders, inventory updates, user accounts
- **Examples**: PostgreSQL, MySQL, Oracle, SQL Server

## Multi-Dimensional Database (MDDB)

- **Structure**: Data is organized in cubes with multiple dimensions - like a sophisticated pivot table
- **Model**: Data is pre-aggregated along various dimensions (time, geography, product category, etc.)
- **Queries**: Uses specialized languages like MDX (Multi-Dimensional Expressions)
- **Optimized for**: Analytical processing (OLAP) - quick analysis and reporting across multiple dimensions
- **Examples**: Microsoft Analysis Services, Oracle OLAP, IBM Cognos

## Key Differences

**Data organization**: Relational databases store detailed, normalized data in flat tables. Multi-dimensional databases store aggregated data in hierarchical structures optimized for analysis.

**Performance**: Relational databases excel at handling many small transactions. Multi-dimensional databases are much faster for complex analytical queries across multiple dimensions.

**Typical use**: Relational databases power operational systems (e-commerce sites, banking apps). Multi-dimensional databases power business intelligence and reporting systems.

In practice, many organizations use both - relational databases for day-to-day operations, then extract that data into multi-dimensional databases (data warehouses) for analysis and reporting.

---
# Storage and Tools
The 2 formats have the data is stored quite differently, and they typically require different tools and approaches to access. Lets break this down:

## Physical Storage Differences

**Relational Database:**
- Stores data in actual table structures on disk
- Each row is a record with values in columns
- Data is normalized (split across tables to avoid redundancy)

**Multi-Dimensional Database:**
- Often stores data as aggregated arrays or specialized cube structures
- Pre-calculates summaries along dimensions
- May use specialized compression for sparse data
- Some implementations actually store the cube metadata while keeping base data in relational tables

## Tool Compatibility

Generally, **you cannot use the same tools** directly on both. They require different query languages and client libraries:

- Relational → SQL
- Multi-dimensional → MDX, DAX, or proprietary languages

## Examples with Code

### Relational Database Example

**Tools:** Python with psycopg2, MySQL Workbench, pgAdmin, DBeaver

```python
import psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="sales_db",
    user="username",
    password="password"
)

cursor = conn.cursor()

# SQL query to get sales by product and region
query = """
    SELECT 
        p.product_name,
        r.region_name,
        SUM(s.sales_amount) as total_sales
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    JOIN regions r ON s.region_id = r.region_id
    WHERE s.sale_date BETWEEN '2024-01-01' AND '2024-12-31'
    GROUP BY p.product_name, r.region_name
    ORDER BY total_sales DESC
"""

cursor.execute(query)
results = cursor.fetchall()

for row in results:
    print(f"Product: {row[0]}, Region: {row[1]}, Sales: ${row[2]:,.2f}")

cursor.close()
conn.close()
```

### Multi-Dimensional Database Example

**Tools:** Microsoft Excel with OLAP connections, Power BI, Tableau, Python with olap libraries

**Example 1: Using MDX (Multi-Dimensional Expressions)**

```python
# Using Python's msolap library or similar
from msolap import Connection

# Connect to OLAP cube
conn = Connection('Provider=MSOLAP;Data Source=localhost;Initial Catalog=SalesCube')

# MDX query to slice the cube
mdx_query = """
    SELECT 
        [Product].[Product Name].Members ON COLUMNS,
        [Geography].[Region].Members ON ROWS
    FROM [Sales Cube]
    WHERE [Time].[Year].[2024]
"""

result = conn.execute(mdx_query)
print(result)
```

**Example 2: Using DAX with Power BI/Tabular Models**

```python
# Using Python's pyadomd library
import pyadomd

conn_str = "Provider=MSOLAP;Data Source=localhost;Initial Catalog=TabularModel"
conn = pyadomd.connect(conn_str)

# DAX query
dax_query = """
    EVALUATE
    SUMMARIZECOLUMNS(
        'Product'[ProductName],
        'Region'[RegionName],
        "Total Sales", SUM('Sales'[SalesAmount])
    )
"""

cursor = conn.cursor()
cursor.execute(dax_query)
results = cursor.fetchall()

for row in results:
    print(row)

conn.close()
```

**Example 3: Using XMLA (the protocol behind OLAP access)**

```python
import requests
import xml.etree.ElementTree as ET

# XMLA request to SSAS
xmla_request = """
<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
  <Body>
    <Execute xmlns="urn:schemas-microsoft-com:xml-analysis">
      <Command>
        <Statement>
          SELECT [Product].[Product].Members ON 0
          FROM [Sales Cube]
        </Statement>
      </Command>
    </Execute>
  </Body>
</Envelope>
"""

response = requests.post(
    'http://localhost/olap/msmdpump.dll',
    data=xmla_request,
    headers={'Content-Type': 'text/xml'}
)
```

## Common BI Tools That Can Access Both

Some modern BI tools act as bridges and can connect to both:

**Tableau:**
```python
# Can connect to both PostgreSQL and SSAS cubes
# Uses different connection types but unified interface
```

**Power BI:**
- Import relational data with SQL
- Connect directly to Analysis Services cubes with DAX/MDX

**Python pandas** (for relational):
```python
import pandas as pd
import sqlalchemy

engine = sqlalchemy.create_engine('postgresql://user:pass@localhost/db')
df = pd.read_sql("SELECT * FROM sales", engine)
```

## The Hybrid Approach

Many organizations use **data warehouses** that combine both approaches:

1. Store detailed data in relational format (star or snowflake schema)
2. Build OLAP cubes on top for fast analytical queries
3. Use ETL tools to move data from operational databases to the warehouse

**Example using SQL Server Analysis Services:**
- Base data in SQL Server (relational)
- SSAS cube built on top (multi-dimensional)
- Query the cube for analysis, query the tables for details

The key takeaway: while you need different query languages and tools for each, modern BI platforms increasingly abstract these differences, letting you work with both through a unified interface.
