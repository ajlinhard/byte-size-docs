# Pandas Copy Data Efficiently
When working with pandas data there are many different needs for managing dataframes efficiently. Understanding different types of copies is crucial for performance and memory management. Here are the main types:

## 1. **Shallow Copy**
**What it is**: Copies the container/structure but not the actual data objects inside it.

**How it works**:
- Creates a new object
- Fills it with references to the original objects
- Changes to the container don't affect the original
- Changes to the contained objects affect both copies

**Use cases**:
- When you want to modify the structure (add/remove items) without affecting the original
- Performance-critical situations where you don't need data isolation
- DataFrame operations where you're adding/removing columns but data stays the same

**Examples**:
```python
import copy
import pandas as pd

# Python lists
original = [[1, 2], [3, 4]]
shallow = copy.copy(original)  # or original.copy()
shallow[0][0] = 999  # Affects original!
print(original)  # [[999, 2], [3, 4]]

# Pandas
df_shallow = df.copy(deep=False)
df_shallow['new_col'] = 123  # Original df unchanged
df_shallow.loc[0, 'existing_col'] = 999  # Original df IS changed
```

## 2. **Deep Copy**
**What it is**: Recursively copies the container AND all objects inside it.

**How it works**:
- Creates completely independent objects
- Changes to either copy don't affect the other
- Much slower and more memory-intensive

**Use cases**:
- When you need complete data isolation
- Working with nested mutable objects
- Creating truly independent backups
- Multi-threading scenarios where data integrity is critical

**Examples**:
```python
# Python
original = [[1, 2], [3, 4]]
deep = copy.deepcopy(original)
deep[0][0] = 999  # Original unchanged
print(original)  # [[1, 2], [3, 4]]

# Pandas
df_deep = df.copy(deep=True)  # Default behavior
# Any changes to df_deep won't affect original df
```

## 3. **Reference/Alias (No Copy)**
**What it is**: Just another name pointing to the same object.

**How it works**:
- No new object created
- Both variables point to identical memory location
- Any changes affect both variables

**Use cases**:
- Maximum performance (no memory/time overhead)
- When you want changes to be reflected everywhere
- Temporary operations where you don't need isolation

**Examples**:
```python
# Python
original = [1, 2, 3]
reference = original  # Not a copy!
reference.append(4)
print(original)  # [1, 2, 3, 4]

# Pandas
df_ref = df  # Same DataFrame object
df_view = df[['col1', 'col2']]  # Often a view, not copy
```

## 4. **Copy-on-Write (COW)**
**What it is**: Smart copying that delays actual copying until modification occurs.

**How it works**:
- Initially acts like a reference
- Automatically creates a copy when either version is modified
- Optimizes memory usage and performance

**Use cases**:
- Modern pandas operations (pandas 2.0+)
- Large datasets where copying might not be necessary
- Functional programming patterns

**Examples**:
```python
# Pandas 2.0+ with COW enabled
df2 = df.copy()  # Fast - no actual copying yet
df2['new_col'] = 1  # Now it actually copies the needed parts
```

## 5. **View (Partial Reference)**
**What it is**: A window into existing data without copying.

**How it works**:
- Shows a subset or transformation of original data
- Usually shares memory with original
- Changes often propagate back to original

**Use cases**:
- Array slicing in NumPy
- DataFrame column selection
- Memory-efficient data analysis

**Examples**:
```python
import numpy as np

# NumPy - views share memory
arr = np.array([1, 2, 3, 4, 5])
view = arr[1:4]  # View, not copy
view[0] = 999
print(arr)  # [1, 999, 3, 4, 5]

# Pandas - sometimes views, sometimes copies
df_subset = df['column']  # Usually a view
df_slice = df.iloc[0:5]   # Usually a view
```

## 6. **Lazy Copy**
**What it is**: Defers copying until actually needed by the computation.

**How it works**:
- Records what needs to be copied
- Only performs the copy when the data is accessed/modified
- Often used in functional data libraries

**Use cases**:
- Large data processing pipelines
- Functional programming libraries (like Polars)
- Memory-constrained environments

## Performance and Memory Trade-offs

| Copy Type | Speed | Memory Usage | Data Safety | Use When |
|-----------|-------|--------------|-------------|----------|
| Reference | Fastest | Minimal | None | Performance critical, no isolation needed |
| Shallow | Fast | Low | Partial | Structural changes, data mostly unchanged |
| View | Fast | Minimal | Depends | Read-mostly operations, memory constrained |
| Deep | Slow | High | Complete | Need full isolation, nested structures |
| COW | Smart | Adaptive | Complete | Modern libraries, uncertain modification patterns |
| Lazy | Variable | Adaptive | Complete | Large datasets, uncertain access patterns |

## In Your Pandas Context

For your original datetime extraction question:
- **Individual assignment**: Creates references to new Series objects (fast)
- **List assignment**: May trigger copying depending on data types (variable speed)
- **assign()**: Always creates a copy + overhead (slower)

The key insight is that understanding these copy types helps you choose the right approach based on your specific performance, memory, and safety requirements!

---
# More About Copy-On-Write(COW)
Great question! Copy-on-Write (COW) in pandas can be enabled in several ways. Let me search for the most current information on how to enable it.Perfect! Based on the search results, here are the different ways to enable Copy-on-Write (COW) in pandas:

## Current Status (as of 2025)
COW is **enabled by default** in pandas 3.0, but for pandas 2.x versions, you need to enable it manually.

## How to Enable COW in pandas 2.0+

### 1. **Runtime Setting (Most Common)**
```python
import pandas as pd

# Enable COW for the current session
pd.options.mode.copy_on_write = True
```

### 2. **Context Manager (Temporary)**
```python
# Enable COW temporarily for specific operations
with pd.option_context("mode.copy_on_write", True):
    df = pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]})
    # COW behavior applies here
    subset = df["foo"]
    subset.iloc[0] = 100  # Won't modify original df
```

### 3. **Check if COW is Enabled**
```python
# Check current COW status
print(pd.options.mode.copy_on_write)  # True or False
```

### 4. **Environment Variable (System-wide)**
You can also set an environment variable before starting Python:
```bash
export PANDAS_COPY_ON_WRITE=1
```

## Key Timeline Information

- **pandas 1.5.0**: COW first introduced
- **pandas 2.0**: Most COW optimizations implemented  
- **pandas 2.1**: All possible optimizations supported
- **pandas 3.0**: COW enabled by default (no manual enabling needed)

## What COW Does

When enabled, COW ensures that any DataFrame or Series derived from another always behaves as a copy, preventing accidental mutations and improving performance by delaying actual copying until modification occurs.

## Example of COW in Action

```python
import pandas as pd

# Without COW (traditional behavior)
pd.options.mode.copy_on_write = False
df = pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]})
subset = df["foo"]
subset.iloc[0] = 100
print(df)  # Original df IS modified! foo[0] = 100

# With COW enabled
pd.options.mode.copy_on_write = True
df = pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]})
subset = df["foo"]
subset.iloc[0] = 100
print(df)  # Original df is NOT modified! foo[0] = 1
```

## Warning Mode
Pandas also has a warning mode that will alert you to operations that will change behavior with COW, though it can be quite noisy.

**Bottom line**: For pandas 2.x, use `pd.options.mode.copy_on_write = True` at the start of your script. For pandas 3.0+, it's already enabled by default!
