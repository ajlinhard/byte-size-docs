# Pandas Correlation Function
A correlation matrix in pandas is a square table that shows the correlation coefficients between pairs of variables in your dataset. Each cell contains a value between -1 and 1 that indicates how strongly two variables are linearly related.

**What the values mean:**
- **1.0**: Perfect positive correlation (as one variable increases, the other increases proportionally)
- **0.0**: No linear correlation (variables are independent)
- **-1.0**: Perfect negative correlation (as one variable increases, the other decreases proportionally)
- Values closer to 1 or -1 indicate stronger relationships

**Creating a correlation matrix in pandas:**
```python
import pandas as pd

# Assuming you have a DataFrame called 'df'
correlation_matrix = df.corr()

# You can also specify the method (default is Pearson)
correlation_matrix = df.corr(method='pearson')  # or 'spearman', 'kendall'
```

**Key characteristics:**
- The diagonal is always 1.0 (each variable perfectly correlates with itself)
- The matrix is symmetric (correlation between A and B equals correlation between B and A)
- Only works with numeric columns by default
- Missing values are automatically excluded from calculations

**Common use cases:**
- Identifying which features are most related to your target variable
- Detecting multicollinearity (highly correlated predictors) before building models
- Understanding relationships between different metrics in your data
- Feature selection by removing highly correlated variables

You can visualize correlation matrices using seaborn's heatmap or pandas' built-in plotting functionality to make patterns easier to spot.

## Code Examples
Here's a comprehensive code example showing how to create and work with correlation matrices in pandas:

```python
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Create sample data
np.random.seed(42)
data = {
    'height': np.random.normal(170, 10, 100),
    'weight': np.random.normal(70, 15, 100),
    'age': np.random.randint(18, 65, 100),
    'income': np.random.normal(50000, 20000, 100),
    'exercise_hours': np.random.normal(5, 2, 100)
}

# Make some variables correlated for demonstration
data['weight'] = data['height'] * 0.8 + np.random.normal(0, 5, 100)  # Height-weight correlation
data['income'] = data['age'] * 800 + np.random.normal(0, 10000, 100)  # Age-income correlation

df = pd.DataFrame(data)

print("Sample data:")
print(df.head())
print("\n" + "="*50 + "\n")

# 1. Basic correlation matrix
print("1. Basic correlation matrix:")
corr_matrix = df.corr()
print(corr_matrix)
print("\n" + "="*50 + "\n")

# 2. Rounded correlation matrix for cleaner display
print("2. Rounded correlation matrix:")
print(corr_matrix.round(3))
print("\n" + "="*50 + "\n")

# 3. Different correlation methods
print("3. Different correlation methods:")
print("Pearson (default):")
print(df.corr(method='pearson').round(3))
print("\nSpearman (rank-based):")
print(df.corr(method='spearman').round(3))
print("\n" + "="*50 + "\n")

# 4. Filter correlations above a threshold
print("4. Strong correlations (absolute value > 0.5):")
strong_corr = corr_matrix[abs(corr_matrix) > 0.5]
print(strong_corr.dropna(how='all').dropna(axis=1, how='all'))
print("\n" + "="*50 + "\n")

# 5. Get correlations with a specific variable
print("5. Correlations with 'weight':")
weight_correlations = corr_matrix['weight'].sort_values(ascending=False)
print(weight_correlations)
print("\n" + "="*50 + "\n")

# 6. Find pairs of highly correlated variables
print("6. Highly correlated pairs (> 0.7):")
# Get upper triangle of correlation matrix to avoid duplicates
upper_triangle = corr_matrix.where(
    np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
)

# Find pairs with high correlation
high_corr_pairs = []
for col in upper_triangle.columns:
    for idx in upper_triangle.index:
        value = upper_triangle.loc[idx, col]
        if abs(value) > 0.7:
            high_corr_pairs.append((idx, col, value))

for pair in high_corr_pairs:
    print(f"{pair[0]} - {pair[1]}: {pair[2]:.3f}")

# 7. Visualize correlation matrix
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, 
            annot=True,           # Show correlation values
            cmap='coolwarm',      # Color scheme
            center=0,             # Center colormap at 0
            square=True,          # Square cells
            fmt='.2f')            # Format numbers to 2 decimal places

plt.title('Correlation Matrix Heatmap')
plt.tight_layout()
plt.show()

# 8. Alternative visualization - just the lower triangle
plt.figure(figsize=(10, 8))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))  # Mask upper triangle
sns.heatmap(corr_matrix, 
            annot=True, 
            mask=mask,
            cmap='coolwarm', 
            center=0,
            square=True, 
            fmt='.2f')

plt.title('Correlation Matrix - Lower Triangle Only')
plt.tight_layout()
plt.show()
```

**Output explanation:**

The code demonstrates several key concepts:

1. **Basic correlation matrix** - Shows all pairwise correlations
2. **Rounding** - Makes the output more readable
3. **Different methods** - Pearson vs Spearman correlations
4. **Filtering** - Find only strong correlations
5. **Specific variable** - Get correlations with one column
6. **High correlation pairs** - Identify potential multicollinearity issues
7. **Visualization** - Heatmap makes patterns obvious

**Key takeaways:**
- Diagonal values are always 1.0 (perfect self-correlation)
- Values close to 1 or -1 indicate strong linear relationships
- Values near 0 suggest little to no linear relationship
- The heatmap visualization makes it much easier to spot patterns than looking at raw numbers

This correlation matrix helps you understand which variables move together in your dataset, which is crucial for feature selection, model building, and data exploration.
