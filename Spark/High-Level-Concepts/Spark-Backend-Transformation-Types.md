# Spark Backend Transformation Types
Spark classifies transformations based on how they affect data distribution and processing patterns.

## **1. Narrow Transformations**

These operate on individual partitions independently - each output partition depends on only **one input partition**.

### Examples:
```python
df.select('shape')           # Projection
df.filter(df.id > 200)       # Filtering  
df.map(lambda x: x.upper())  # Element-wise operations
df.withColumn("new", df.id * 2)  # Column operations
df.drop('id')                # Column removal
```

### Characteristics:
- **No shuffle required** - data stays in same partition
- **Fast execution** - processed locally on each executor
- **Pipeline-able** - multiple narrow transformations can be combined
- **Fault tolerance** - easy to recompute if partition is lost

## **2. Wide Transformations (Shuffle Transformations)**

These require data from **multiple input partitions** to compute output partitions.

### Examples:
```python
df.groupBy('shape').count()              # Aggregation
df.orderBy('id')                         # Global sorting
df1.join(df2, 'key')                     # Joins
df.distinct()                            # Deduplication
df.repartition(10)                       # Repartitioning
```

### Characteristics:
- **Shuffle required** - data moves across network between executors
- **Expensive** - involves disk I/O and network transfer
- **Stage boundaries** - create new stages in execution plan
- **Fault tolerance cost** - harder to recompute, may need to recompute upstream

## **Backend Processing Differences**

### Narrow Transformation Pipeline:
```
Partition 1: [123,'circle'] → select('shape') → ['circle']
Partition 2: [324,'square'] → select('shape') → ['square']  
Partition 3: [345,'triangle'] → select('shape') → ['triangle']
```
*Each partition processed independently, no data movement*

### Wide Transformation Example:
```python
df.groupBy('shape').count()
```

**Stage 1** (Map phase):
```
Partition 1: [123,'circle'] → hash('circle') → shuffle write
Partition 2: [324,'square'] → hash('square') → shuffle write
Partition 3: [345,'triangle'] → hash('triangle') → shuffle write
```

**Shuffle**: Data redistributed by hash key

**Stage 2** (Reduce phase):
```
New Partition 1: All 'circle' records → count() → ['circle', 1]
New Partition 2: All 'square' records → count() → ['square', 1]
New Partition 3: All 'triangle' records → count() → ['triangle', 1]
```

## **How Spark Optimizes This**

### Catalyst Optimizer:
- **Predicate pushdown**: Moves filters early in the plan
- **Projection pushdown**: Reduces columns read from storage
- **Combines narrow transformations**: Creates efficient pipelines

### Example optimization:
```python
# Your code:
df.select('shape').filter(df.shape != 'circle').select('shape')

# Spark optimizes to:
df.filter(df.shape != 'circle').select('shape')  # Combined pipeline
```

The key insight is that **narrow transformations are cheap and pipelined**, while **wide transformations are expensive and create stage boundaries** where Spark must materialize intermediate results and shuffle data across the cluster.
