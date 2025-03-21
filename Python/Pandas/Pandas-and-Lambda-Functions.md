```python
import pandas as pd
import numpy as np

# Create a sample DataFrame
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Emma'],
    'Age': [25, 30, 35, 40, 45],
    'Salary': [50000, 60000, 75000, 90000, 85000],
    'Department': ['HR', 'IT', 'Finance', 'IT', 'Marketing'],
    'Experience': [2, 5, 8, 12, 7]
})

print("Original DataFrame:")
print(df)
print("\n")

# Example 1: Using lambda to transform a single column
# Convert names to uppercase
df['Name'] = df['Name'].apply(lambda x: x.upper())

# Example 2: Using lambda to create a new column based on existing column
# Calculate bonus based on salary (10% of salary)
df['Bonus'] = df['Salary'].apply(lambda x: x * 0.1)

# Example 3: Using lambda with multiple conditions
# Create a category based on age
df['Age_Category'] = df['Age'].apply(lambda x: 'Young' if x < 30 else ('Middle-aged' if x < 40 else 'Senior'))

# Example 4: Using lambda with multiple columns
# Calculate adjusted salary based on experience (2% increase per year of experience)
df['Adjusted_Salary'] = df.apply(lambda row: row['Salary'] * (1 + 0.02 * row['Experience']), axis=1)

# Example 5: Using lambda to conditionally format values
# Format salary with currency symbol and commas
df['Formatted_Salary'] = df['Salary'].apply(lambda x: f"${x:,}")

# Example 6: Using lambda with np.where (vectorized if-else)
# Set department priority (IT and Finance are high priority)
df['Dept_Priority'] = np.where(
    df['Department'].apply(lambda x: x in ['IT', 'Finance']),
    'High',
    'Standard'
)

print("Transformed DataFrame:")
print(df)

```

Here I've created an example showing several ways to use lambda functions with pandas for column transformations:

1. Single column transformation: Converting names to uppercase
2. Creating a new column: Calculating a bonus amount based on salary
3. Conditional logic: Categorizing ages into groups
4. Row-wise operations: Calculating adjusted salary based on experience years
5. String formatting: Adding currency symbols and formatting to salary
6. Vectorized operations: Setting department priorities using `np.where`

Each example demonstrates a different pattern for using lambda functions with pandas. Lambda functions are particularly useful for quick, one-off transformations without defining a separate named function.

Would you like me to explain any of these transformations in more detail or show other types of column transformations using lambda functions?

## Lambda and Apply Efficency Concerns:
Lambda functions in pandas transformations are convenient but not always the most efficient approach. Here's a breakdown:

### When lambda functions might not be optimal:

1. **Performance concerns**: 
   - `.apply()` with lambda functions can be slow for large DataFrames because it iterates row by row in Python rather than using optimized C code
   - For large datasets, this can create significant performance bottlenecks

2. **Vectorized operations are faster**:
   - Native pandas methods and NumPy functions that operate on entire columns at once are much faster
   - Example: `df['Salary'] * 0.1` is faster than `df['Salary'].apply(lambda x: x * 0.1)`

3. **Readability in complex cases**:
   - Complex lambda functions can become hard to read and maintain
   - Named functions often better document your intent

### Better alternatives:

1. **Vectorized operations**:
   ```python
   # Instead of:
   df['Bonus'] = df['Salary'].apply(lambda x: x * 0.1)
   
   # Use:
   df['Bonus'] = df['Salary'] * 0.1
   ```

2. **NumPy functions**:
   ```python
   # Instead of:
   df['Squared'] = df['Value'].apply(lambda x: x**2)
   
   # Use:
   df['Squared'] = np.square(df['Value'])
   ```

3. **pandas built-in methods**:
   ```python
   # Instead of:
   df['Name_Upper'] = df['Name'].apply(lambda x: x.upper())
   
   # Use:
   df['Name_Upper'] = df['Name'].str.upper()
   ```

4. **Named functions for complex transformations**:
   ```python
   def categorize_age(age):
       if age < 30:
           return 'Young'
       elif age < 40:
           return 'Middle-aged'
       else:
           return 'Senior'
   
   df['Age_Category'] = df['Age'].apply(categorize_age)
   ```

5. **numpy.where/numpy.select for conditional logic**:
   ```python
   # Better than apply+lambda for conditionals:
   df['Age_Category'] = np.select(
       [df['Age'] < 30, df['Age'] < 40],
       ['Young', 'Middle-aged'],
       default='Senior'
   )
   ```

Lambda functions are still useful for quick, simple transformations during exploration, but for production code or large datasets, the vectorized alternatives are almost always preferable for both performance and readability.
