# Spark Backend Transformation Types
Spark classifies transformations based on how they affect data distribution and processing patterns.

[Jump To: Deep Dive into Spark Transformation Types](#Deep-Dive-into-Spark-Transformation-Types)

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

---
# Deep Dive into Spark Transformation Types
---

## **1. Narrow Transformations**

### **What Makes Them "Narrow"**
A transformation is narrow when each **output partition** is computed from **exactly one input partition**. There's a 1:1 or many:1 relationship between input and output partitions, but never 1:many.

### **Core Characteristics Explained**

#### **No Shuffle Required**
```python
# Example: filter transformation
df = spark.createDataFrame([(1, 'A'), (2, 'B'), (3, 'C')], ['id', 'letter'])
filtered_df = df.filter(df.id > 1)
```

**Why no shuffle?** Each executor can look at its local partitions and decide which records to keep/discard without needing data from other partitions.

```
Executor 1: Partition 0: [(1,'A'), (2,'B')] → filter(id>1) → [(2,'B')]
Executor 2: Partition 1: [(3,'C')]           → filter(id>1) → [(3,'C')]
Executor 3: Partition 2: []                  → filter(id>1) → []
```

#### **Pipelining (Operator Fusion)**
Multiple narrow transformations can be combined into a single stage:

```python
result = df.select('id', 'letter') \
          .filter(df.id > 1) \
          .withColumn('doubled_id', df.id * 2) \
          .drop('letter')
```

**Backend execution**: All these operations happen in one pass through the data on each partition - no intermediate materialization needed.

#### **Fast Fault Recovery**
If Partition 2 on Executor 3 fails:
- Only need to recompute that specific partition
- Can use lineage to trace back to source data
- No need to recompute other partitions

### **Types of Narrow Transformations**

#### **1. Element-wise Operations**
```python
df.select('col1')                    # Projection
df.withColumn('new', df.col1 * 2)    # Column operations
df.filter(df.age > 21)               # Row filtering
df.map(lambda row: row.upper())      # Element transformation
```

#### **2. Union (Special Case)**
```python
df1.union(df2)
```
This is narrow because output partition N = input partition N from df1 + input partition N from df2. No cross-partition dependencies.

### **Performance Implications**
- **Memory efficient**: Processes records one at a time
- **CPU bound**: Limited by processing speed, not I/O
- **Parallelizable**: Perfect linear scaling with more executors

---

## **2. Wide Transformations (Shuffle Operations)**

### **What Makes Them "Wide"**
Each output partition potentially depends on **multiple input partitions**. This creates many:many relationships that require data movement.

### **Core Characteristics Explained**

#### **Shuffle Requirement Deep Dive**

```python
df.groupBy('department').sum('salary')
```

**Why shuffle is needed:**
```
Initial partitions (random distribution):
Partition 0: [('Engineering', 100), ('Sales', 80)]
Partition 1: [('Engineering', 120), ('Marketing', 90)]  
Partition 2: [('Sales', 95), ('Engineering', 110)]

After shuffle (grouped by key):
Partition 0: [('Engineering', 100), ('Engineering', 120), ('Engineering', 110)]
Partition 1: [('Sales', 80), ('Sales', 95)]
Partition 2: [('Marketing', 90)]
```

#### **The Shuffle Process (5 Phases)**

**Phase 1: Map Side Preparation**
```python
# Each partition computes hash(key) % num_output_partitions
# Creates shuffle files on local disk
```

**Phase 2: Shuffle Write**
- Each mapper writes shuffle files (one per reducer)
- Files stored on executor's local disk
- Includes index files for efficient reading

**Phase 3: Shuffle Service**
- External shuffle service (or executor) serves shuffle files
- Handles requests from other executors
- Provides fault tolerance if executor dies

**Phase 4: Shuffle Read**  
- Reducers fetch their data from all mappers
- Network transfer across cluster
- Can be bottlenecked by network bandwidth

**Phase 5: Shuffle Aggregation**
- Final computation (grouping, sorting, etc.)
- Happens on reducer side

#### **Stage Boundaries**
Wide transformations create **stage boundaries** because:
- All upstream tasks must complete before shuffle can begin
- Creates natural checkpoints in execution
- Enables independent retry of stages

### **Types of Wide Transformations**

#### **1. Aggregation-based**
```python
df.groupBy('key').agg({'value': 'sum'})     # Hash-based grouping
df.rollup('col1', 'col2').count()           # Hierarchical aggregation  
df.cube('col1', 'col2').sum('value')        # Multi-dimensional aggregation
```

**Shuffle pattern**: Hash partitioning by group key

#### **2. Join Operations**
```python
df1.join(df2, 'key', 'inner')
```

**Shuffle patterns vary by join strategy:**
- **Sort-merge join**: Both sides sorted by join key
- **Broadcast hash join**: Smaller table broadcasted (no shuffle for small table)
- **Shuffle hash join**: Both sides hash partitioned

#### **3. Sorting**
```python
df.orderBy('column')
```
**Why wide?** Global ordering requires seeing all data to determine correct sort order.

**Process:**
1. Sample data to determine range partitions
2. Shuffle data into range-partitioned buckets  
3. Sort within each partition

#### **4. Set Operations**
```python
df1.intersect(df2)    # Find common records
df1.subtract(df2)     # Records in df1 but not df2
```

**Why wide?** Need to compare every record in df1 against every record in df2.

#### **5. Repartitioning**
```python
df.repartition(10)              # Change partition count
df.repartition('column')        # Partition by column values
df.coalesce(5)                  # Reduce partitions (narrow if reducing)
```

### **Performance Implications**

#### **Network Bottlenecks**
```python
# Bad: Multiple wide transformations
df.groupBy('col1').count() \
  .join(df2, 'col1') \
  .orderBy('count')

# Each operation triggers separate shuffle!
```

#### **Disk I/O Impact**
- Shuffle spills to disk when memory full
- Configurable via `spark.sql.shuffle.partitions`
- Default 200 partitions often too high for small datasets

#### **Memory Pressure**
```python
# This can cause OOM if groups are very large
df.groupBy('skewed_key').collect_list('large_column')
```

---

## **3. Special Categories & Edge Cases**

### **Coalesce vs Repartition**

#### **Coalesce (Sometimes Narrow)**
```python
df.coalesce(5)  # Reduce from 10 to 5 partitions
```

**When narrow?** Reducing partitions - can combine existing partitions without full shuffle.

**When wide?** Increasing partitions - requires redistributing data.

#### **Repartition (Always Wide)**
```python
df.repartition(5)  # Always triggers full shuffle
```

### **Broadcast Variables & Map-side Joins**

#### **Broadcast Hash Join**
```python
# If df2 is small (< spark.sql.adaptive.autoBroadcastJoinThreshold)
large_df.join(small_df, 'key')
```

**Optimization**: Small table broadcasted to all executors, making join narrow!

### **Bucketed Tables**

```python
# Pre-partitioned tables can make joins narrow
df.write.bucketBy(10, 'key').saveAsTable('bucketed_table')

# Join between bucketed tables on bucket key = narrow transformation!
bucketed_df1.join(bucketed_df2, 'key')
```

---

## **4. Advanced Optimization Techniques**

### **Catalyst Optimizer Transformations**

#### **Predicate Pushdown**
```python
# Your code:
df.join(df2, 'key').filter(df.value > 100)

# Catalyst optimizes to:
df.filter(df.value > 100).join(df2, 'key')  # Filter before expensive join
```

#### **Projection Pushdown**
```python
# Your code:
df.join(df2, 'key').select('needed_col')

# Catalyst optimizes to:
df.select('key', 'needed_col').join(df2.select('key'), 'key')
```

### **Adaptive Query Execution (AQE)**

#### **Dynamic Coalescing**
- Automatically reduces partition count for small data
- Prevents too many small tasks

#### **Dynamic Join Strategy**
- Switches join strategies based on runtime statistics
- Can convert sort-merge to broadcast join

#### **Skew Join Optimization**
- Detects data skew during execution
- Splits large partitions automatically

---

## **5. Practical Performance Guidelines**

### **Choosing Partition Count**
```python
# Rule of thumb: 2-4 tasks per CPU core
num_partitions = num_cores * 2 to 4

# For shuffles, consider data size
# ~128MB - 1GB per partition is optimal
target_partition_size = total_data_size / (128 * 1024 * 1024)  # 128MB chunks
```

### **Memory Tuning**
```python
# Increase memory for shuffle-heavy workloads
spark.conf.set("spark.sql.shuffle.partitions", "400")
spark.conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
spark.conf.set("spark.sql.adaptive.enabled", "true")
```

### **Monitoring Shuffles**
- Watch Spark UI's "Shuffle Read/Write" metrics
- High shuffle read time = network bottleneck
- High shuffle write time = disk bottleneck
- Large shuffle spill = memory pressure

Understanding these transformation types is crucial for writing efficient Spark applications, as the choice between narrow and wide operations can dramatically impact performance, especially at scale.
