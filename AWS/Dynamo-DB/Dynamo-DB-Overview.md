# Dynamo DB Overview
Dynamo DB is the AWS offering of a NoSQL database. It has the classic good integrations with other AWS Services and NoSQLs highly transactional nature.

### Documentation and Tutorials

---
## NoSQL Indexes
DynamoDB uses several types of indexes to enable efficient data access patterns beyond the primary key. Here's how they work:

## Primary Key (Base Table)
Every DynamoDB table must have a primary key, which can be:
- **Partition Key only** - Items distributed across partitions based on this key's hash
- **Composite Key** - Partition key + sort key, allowing multiple items with the same partition key

## Global Secondary Index (GSI)
A GSI creates a completely separate index with its own partition and sort keys, different from the base table:

- **Independent key schema** - Can use any attributes as partition/sort keys
- **Separate provisioned throughput** - Has its own read/write capacity settings
- **Eventually consistent** - Updates propagate asynchronously from base table
- **Sparse index** - Only includes items that have the GSI key attributes
- **Cross-partition queries** - Can query across all partitions in the GSI

Example: Base table uses `UserID` as partition key, but you create a GSI with `Email` as partition key to enable email-based lookups.

## Local Secondary Index (LSI)
An LSI shares the same partition key as the base table but uses a different sort key:

- **Same partition key** - Must use the base table's partition key
- **Different sort key** - Can sort items differently within each partition
- **Strongly consistent reads** - Can provide strong consistency since data is co-located
- **Shared throughput** - Uses the base table's provisioned capacity
- **Must be created at table creation** - Cannot be added later
- **10GB limit per partition** - All LSIs and base table items combined

Example: Base table has `UserID` (partition) + `Timestamp` (sort), LSI uses `UserID` (partition) + `Priority` (sort) to query user items by priority.

## Key Differences

**GSI vs LSI:**
- GSIs can use any attributes as keys; LSIs must use the base table's partition key
- GSIs are eventually consistent; LSIs can be strongly consistent
- GSIs have separate capacity; LSIs share base table capacity
- GSIs can be added after table creation; LSIs cannot

**Projection:**
Both index types let you specify which attributes to include:
- `KEYS_ONLY` - Just the key attributes
- `INCLUDE` - Keys plus specified non-key attributes  
- `ALL` - All attributes from base table items

## Query Patterns
- Use GSIs when you need to query by attributes other than the primary key
- Use LSIs when you need different sort orders within the same partition key
- Indexes enable efficient queries but add storage costs and complexity

The choice between GSI and LSI depends on your access patterns, consistency requirements, and whether you need to query across partitions or just within them.
