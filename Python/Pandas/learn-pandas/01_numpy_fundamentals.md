# NumPy Fundamentals

NumPy underpins pandas — every pandas column is (usually) a NumPy array under
the hood. Understanding NumPy makes pandas's performance quirks make sense.

```python
import numpy as np
```

---

## 1. Why NumPy over plain Python lists

- Contiguous, typed memory → fast, cache-friendly operations.
- **Vectorization**: operations apply to whole arrays without explicit
  Python-level loops (loops run in compiled C instead).
- Broadcasting lets you combine arrays of different shapes without manual
  reshaping.

```python
import time

py_list = list(range(1_000_000))
np_arr = np.arange(1_000_000)

# Python loop
t0 = time.time()
py_result = [x * 2 for x in py_list]
t_py = time.time() - t0

# NumPy vectorized
t0 = time.time()
np_result = np_arr * 2
t_np = time.time() - t0

print(t_py, t_np)  # -> NumPy is typically 20-100x faster
```

---

## 2. Creating Arrays

```python
np.array([1, 2, 3])                  # from a list
np.array([[1, 2], [3, 4]])            # 2D from nested lists
np.zeros((3, 4))                      # 3x4 of zeros
np.ones((2, 2))                       # 2x2 of ones
np.full((2, 2), 7)                    # 2x2 filled with 7
np.eye(3)                             # 3x3 identity matrix
np.arange(0, 10, 2)                   # -> [0 2 4 6 8], like range()
np.linspace(0, 1, 5)                  # -> 5 evenly spaced points in [0,1]
np.empty((2, 3))                      # uninitialized (fast but garbage values)
np.array([1, 2, 3], dtype=np.float32) # explicit dtype
```

---

## 3. Array Attributes

```python
arr = np.array([[1, 2, 3], [4, 5, 6]])

arr.shape       # -> (2, 3)
arr.ndim        # -> 2
arr.size        # -> 6  (total elements)
arr.dtype       # -> dtype('int64')
arr.itemsize    # -> 8  (bytes per element)
arr.nbytes      # -> 48 (itemsize * size)
```

---

## 4. Data Types (dtype)

| dtype | Meaning |
|---|---|
| `int8/16/32/64` | signed integers of various widths |
| `uint8/16/32/64` | unsigned integers |
| `float16/32/64` | floating point |
| `bool` | True/False |
| `object` | fallback — arbitrary Python objects (slow, avoid when possible) |
| `str_` / `<U10` | fixed-width unicode strings |

```python
arr = np.array([1, 2, 3])
arr.astype(np.float64)      # cast to float
arr.astype(np.int8)         # narrow dtype — risk of overflow/truncation

# Gotcha: integer overflow is silent, not an error
np.array([200], dtype=np.int8) + np.array([100], dtype=np.int8)  # -> wraps around
```

---

## 5. Indexing & Slicing

```python
arr = np.arange(10)          # [0 1 2 3 4 5 6 7 8 9]

arr[0]                       # -> 0
arr[-1]                      # -> 9
arr[2:5]                     # -> [2 3 4]
arr[::2]                     # -> [0 2 4 6 8]  (stride)
arr[::-1]                    # -> reversed

grid = np.arange(12).reshape(3, 4)
grid[1, 2]                   # -> element at row 1, col 2
grid[0, :]                   # -> entire row 0
grid[:, 1]                   # -> entire column 1
grid[0:2, 1:3]                # -> sub-matrix (rows 0-1, cols 1-2)
```

### Fancy indexing & boolean masking

```python
arr = np.array([10, 20, 30, 40, 50])

arr[[0, 2, 4]]                # fancy indexing -> [10 30 50]
arr[arr > 25]                 # boolean mask -> [30 40 50]
arr[(arr > 15) & (arr < 45)]  # combine conditions with & / | (not `and`/`or`)

np.where(arr > 25, arr, 0)    # -> [0 0 30 40 50] (conditional replace)
```

**Gotcha:** `&`/`|` need parentheses around each condition because of
operator precedence: `arr > 15 & arr < 45` will error or misbehave.

---

## 6. Reshaping & Manipulating

```python
arr = np.arange(12)

arr.reshape(3, 4)             # new shape, same data (view when possible)
arr.reshape(3, -1)            # -1 = "infer this dimension"
arr.reshape(3, 4).ravel()     # flatten to 1D (view if possible)
arr.reshape(3, 4).flatten()   # flatten to 1D (always a copy)
arr.reshape(3, 4).T           # transpose
np.expand_dims(arr, axis=0)   # add a new axis -> shape (1, 12)
np.squeeze(arr.reshape(1, 12))# remove axes of length 1
```

---

## 7. Combining & Splitting Arrays

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

np.concatenate([a, b])            # -> [1 2 3 4 5 6]
np.vstack([a, b])                 # stack as rows -> shape (2, 3)
np.hstack([a, b])                 # stack horizontally -> [1 2 3 4 5 6]
np.stack([a, b], axis=0)          # like vstack, new axis
np.split(np.arange(9), 3)         # -> 3 equal arrays
np.array_split(np.arange(10), 3)  # allows uneven splits
```

---

## 8. Vectorized Operations & Broadcasting

```python
a = np.array([1, 2, 3])
b = np.array([10, 20, 30])

a + b            # element-wise -> [11 22 33]
a * b            # element-wise -> [10 40 90]
a ** 2           # -> [1 4 9]

# Broadcasting: smaller array is "stretched" to match the larger one
matrix = np.ones((3, 3))
row = np.array([1, 2, 3])
matrix + row      # row is broadcast across all 3 rows

col = np.array([[1], [2], [3]])
matrix + col      # col is broadcast across all 3 columns
```

**Broadcasting rule:** compare shapes from the right; dimensions are
compatible if they're equal or one of them is 1.

```
(3, 3) + (3,)   -> (3,) becomes (1, 3), broadcasts to (3, 3)   OK
(3, 3) + (3, 1) -> broadcasts to (3, 3)                        OK
(3, 3) + (2,)   -> incompatible                                ERROR
```

---

## 9. Universal Functions (ufuncs)

```python
arr = np.array([1, 4, 9, 16])

np.sqrt(arr)      # -> [1 2 3 4]
np.exp(arr)       # e^x element-wise
np.log(arr)       # natural log
np.log10(arr)
np.sin(arr); np.cos(arr); np.tan(arr)
np.abs(np.array([-1, -2, 3]))
np.round(np.array([1.234, 5.678]), 1)   # -> [1.2 5.7]
np.clip(arr, 2, 10)                     # cap values to [2, 10]
```

---

## 10. Aggregations

```python
arr = np.array([[1, 2, 3], [4, 5, 6]])

arr.sum()              # -> 21 (all elements)
arr.sum(axis=0)        # -> [5 7 9]   (sum down each column)
arr.sum(axis=1)        # -> [6 15]    (sum across each row)
arr.mean(); arr.std(); arr.var()
arr.min(); arr.max()
arr.argmin(); arr.argmax()   # index of min/max
np.median(arr)
np.percentile(arr, 90)
np.cumsum(arr)         # running total
np.cumprod(arr)        # running product
```

**Axis mental model:** `axis=0` collapses rows (moves *down*), `axis=1`
collapses columns (moves *across*). This exact convention carries over to
pandas `.sum(axis=...)`.

---

## 11. Linear Algebra

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

A @ B                  # matrix multiplication (preferred)
np.dot(A, B)           # equivalent to @
A.T                    # transpose
np.linalg.inv(A)       # inverse
np.linalg.det(A)       # determinant
np.linalg.eig(A)       # eigenvalues/eigenvectors
np.linalg.solve(A, np.array([1, 2]))  # solve Ax = b
np.linalg.norm(np.array([3, 4]))      # -> 5.0 (Euclidean norm)
```

---

## 12. Random Module (modern Generator API)

```python
rng = np.random.default_rng(seed=42)   # preferred over legacy np.random.seed

rng.random(5)                 # 5 floats in [0, 1)
rng.integers(0, 10, size=5)   # 5 ints in [0, 10)
rng.normal(loc=0, scale=1, size=5)     # standard normal samples
rng.choice([1, 2, 3, 4], size=3, replace=False)
rng.shuffle(arr)              # in-place shuffle
```

`np.random.seed(42)` still works but is legacy; `default_rng` gives each
generator its own independent, reproducible state — safer in parallel code.

---

## 13. Views vs Copies

```python
arr = np.arange(10)
view = arr[2:5]       # slicing -> VIEW (shares memory)
view[0] = 999
arr                    # -> arr is also changed!

copy = arr[2:5].copy() # explicit copy -> independent memory
```

**Gotcha:** basic slicing returns a *view*; fancy indexing (lists/boolean
masks) returns a *copy*. This distinction is the root of many pandas
`SettingWithCopyWarning` bugs later on.

---

## 14. Performance Tips

- Prefer vectorized ops (`arr * 2`) over Python `for` loops.
- Avoid `np.append` in a loop (it reallocates every call) — build a list and
  `np.array()` it once, or preallocate with `np.zeros`.
- Use the narrowest dtype that safely fits your data (`float32` vs `float64`)
  to halve memory when precision allows.
- `np.where`, `np.select`, and boolean masks replace most `if/else` loops.

```python
# Multi-condition vectorized branching
arr = np.array([1, -2, 3, -4, 5])
np.select(
    [arr > 0, arr < 0],
    ["positive", "negative"],
    default="zero"
)
```

---

## 15. Common Pitfalls

| Pitfall | Fix |
|---|---|
| `==` on floats (`0.1 + 0.2 == 0.3` is `False`) | use `np.isclose(a, b)` |
| Mutating a view thinking it's independent | `.copy()` explicitly when needed |
| `and`/`or` on arrays | use `&`/`\|` with parentheses, or `np.logical_and/or` |
| Silent integer overflow with narrow dtypes | pick a wide-enough dtype, or check bounds |
| Mixing `object` dtype arrays (slow) | keep dtypes homogeneous where possible |

**Next:** `02_pandas_basics.md` — pandas builds labeled, heterogeneous
tables on top of these same array mechanics.
