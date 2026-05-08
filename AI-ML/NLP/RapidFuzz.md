# Rapid Fuzz Overview

RapidFuzz is a fast, MIT-licensed fuzzy string matching library — a drop-in replacement for the older `fuzzywuzzy` library, but significantly faster and without licensing issues.

## Installation

```bash
pip install rapidfuzz
```

---

## Core Concepts

RapidFuzz is built around **string similarity metrics**. The score returned is always a float from **0 to 100** (not 0–1).

---

## 1. Basic Similarity Scoring

```python
from rapidfuzz import fuzz

fuzz.ratio("hello world", "hello word")        # ~95.2 — simple character overlap
fuzz.partial_ratio("hello", "hello world")     # 100.0 — substring match
fuzz.token_sort_ratio("world hello", "hello world")   # 100.0 — order-independent
fuzz.token_set_ratio("the quick brown fox", "quick brown fox")  # 100.0 — subset-tolerant
```

**When to use which:**

| Function | Best for |
|---|---|
| `ratio` | Short strings, exact-ish matches |
| `partial_ratio` | One string is a substring of the other |
| `token_sort_ratio` | Same words, different order |
| `token_set_ratio` | One string is a subset of the other's words |

---

## 2. Finding the Best Match (`process` module)

The `process` module is where RapidFuzz really shines — matching one query against a list of choices.

```python
from rapidfuzz import process, fuzz

choices = ["New York", "Los Angeles", "Chicago", "New Orleans", "Newark"]

# Find the single best match
best = process.extractOne("New Yok", choices)
# → ('New York', 90.32, 0)  — (match, score, index)

# Find top N matches
top3 = process.extract("New", choices, limit=3)
# → [('New York', 90.0, 0), ('New Orleans', 86.2, 3), ('Newark', 83.3, 4)]
```

---

## 3. Filtering by Score Threshold

```python
# Only return matches above a score cutoff
results = process.extract("Chcago", choices, score_cutoff=70)
# → [('Chicago', 92.3, 2)]

# extractOne also respects cutoff — returns None if no match qualifies
match = process.extractOne("xyz123", choices, score_cutoff=80)
# → None
```

---

## 4. Choosing a Scorer

You can swap the underlying metric:

```python
process.extractOne("new york city", choices, scorer=fuzz.partial_ratio)
process.extractOne("new york city", choices, scorer=fuzz.token_set_ratio)
```

---

## 5. Working with Dictionaries / Custom Keys

```python
from rapidfuzz import process

users = {1: "Alice Johnson", 2: "Bob Smith", 3: "Alicia Keys"}

match = process.extractOne("Alicia Johnson", users)
# → ('Alice Johnson', 85.7, 1)  — returns (value, score, key)
```

---

## 6. CDist — Comparing All Pairs (Matrix)

Great for deduplication or clustering:

```python
from rapidfuzz.process import cdist

strings = ["apple", "appel", "orange", "ornge", "banana"]
matrix = cdist(strings, strings, scorer=fuzz.ratio)
# Returns a numpy matrix of all pairwise scores
print(matrix)
```

---

## 7. Real-World Example: Fuzzy Search on a Dataset

```python
import pandas as pd
from rapidfuzz import process, fuzz

products = pd.DataFrame({
    "name": ["iPhone 15 Pro", "Samsung Galaxy S24", "Google Pixel 8", "OnePlus 12"]
})

query = "iphone pro 15"

match_name, score, idx = process.extractOne(
    query,
    products["name"],
    scorer=fuzz.token_sort_ratio
)

print(f"Best match: {match_name} (score: {score:.1f})")
# → Best match: iPhone 15 Pro (score: 100.0)
```

---

## Performance Tips

- **Use `score_cutoff`** — it short-circuits computation and is much faster on large lists.
- **`process.cdist`** uses parallelism internally; prefer it over manual loops for bulk comparisons.
- RapidFuzz uses **C extensions** under the hood — avoid wrapping it in unnecessary Python loops when processing thousands of strings.

---

## Quick Scorer Cheatsheet

```
ratio              → strict character similarity
partial_ratio      → substring matching
token_sort_ratio   → word-order independent
token_set_ratio    → handles extra/missing words well
WRatio             → auto-picks the best of the above (slower but smart)
```

`WRatio` is a good default if you're unsure which scorer to use — it intelligently combines the others based on input length and characteristics.
