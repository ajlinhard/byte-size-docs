# Postgre Vector Database Setup

### Yes, You Can Turn Your locally or on RDS PostgreSQL Database into a Vector Database!

AWS RDS for PostgreSQL supports the pgvector extension, which allows you to store embeddings from machine learning models and perform efficient similarity searches. This effectively turns your existing PostgreSQL database into a vector database without needing to migrate to a separate system.

## Requirements

**PostgreSQL Version:** pgvector is available on all RDS database instances running PostgreSQL 15.2 and higher. For older versions:
- PostgreSQL 12.19+, 13.15+, 14.12+, 15.7+, and 16.3+ all support pgvector

**Current pgvector Version:** AWS RDS now supports pgvector 0.8.0, which includes improvements to query performance and filtering capabilities.

## How to Enable pgvector

The process is straightforward and doesn't require any complex setup:

### Step 1: Verify Your PostgreSQL Version
First, check that you're running PostgreSQL 15.2 or higher. If you're on an older version, you'll need to upgrade your RDS instance.

### Step 2: Connect to Your Database
Connect to your RDS PostgreSQL instance using any PostgreSQL client (psql, pgAdmin, DBeaver, etc.).

### Step 3: Enable the Extension
Run the following SQL command to enable pgvector:

```sql
CREATE EXTENSION vector;
```

**Important Note:** The extension name is "vector", not "pgvector". This is a common source of confusion.

### Step 4: Verify Installation
Verify the extension is installed by running:

```sql
SELECT typname FROM pg_type WHERE typname = 'vector';
```

This should return "vector" if successful.

## Using pgvector

Once enabled, you can start working with vector data:

### Create a Table with Vector Columns
```sql
-- Create a table with a vector column (e.g., 384 dimensions for embeddings)
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    embedding VECTOR(384)
);
```

### Insert Vector Data
```sql
INSERT INTO products (name, description, embedding) 
VALUES ('Product A', 'Description here', '[0.1, 0.2, 0.3, ...]');
```

### Perform Similarity Searches
```sql
-- Find nearest neighbors using L2 distance
SELECT * FROM products 
ORDER BY embedding <-> '[query_vector_here]' 
LIMIT 5;

-- Cosine distance
SELECT * FROM products 
ORDER BY embedding <=> '[query_vector_here]' 
LIMIT 5;

-- Inner product
SELECT * FROM products 
ORDER BY embedding <#> '[query_vector_here]' 
LIMIT 5;
```

### Create Indexes for Performance
pgvector supports HNSW indexing for low-latency similarity searches with highly relevant results:

```sql
-- Create HNSW index (recommended for most use cases)
CREATE INDEX ON products 
USING hnsw (embedding vector_cosine_ops);

-- Or IVFFlat index
CREATE INDEX ON products 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);
```

## Integration with ML Services

pgvector can store and search embeddings from Amazon Bedrock, Amazon SageMaker, and other ML services. You can generate embeddings using these services and store them directly in your RDS database.

## Key Benefits

1. **No Migration Required** - Your existing RDS database becomes vector-capable
2. **All PostgreSQL Features** - You retain ACID compliance, JOINs, transactions, backups, and all standard PostgreSQL functionality
3. **Unified Data Model** - Store vectors alongside your relational data
4. **Familiar Tools** - Use the same database tools and ORMs you already use
5. **Managed Service** - AWS handles backups, updates, and infrastructure

## Important Notes

- You typically don't need to modify the "shared_preload_libraries" parameter on AWS RDS - the extension works out of the box
- If you need to upgrade pgvector versions in the future, you may need to upgrade your PostgreSQL version first to access newer pgvector releases
- Consider your vector dimensions and dataset size when choosing index types and parameters

This makes it incredibly easy to add vector search capabilities to your existing applications without setting up a separate vector database!
