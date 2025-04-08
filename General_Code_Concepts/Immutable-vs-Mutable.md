# Immutable vs. Mutable
In Python, the difference between mutable and immutable objects is fundamental to understanding how data is handled:

## Immutable Objects

Immutable objects cannot be changed after they are created. Any operation that appears to modify an immutable object actually creates a new object.

**Immutable types in Python include:**
- Integers
- Floats
- Strings
- Tuples
- Frozensets
- Booleans

For example, with strings:
```python
s = "hello"
s = s + " world"  # Creates a new string object
```

## Mutable Objects

Mutable objects can be modified after creation. Operations can change their content without creating a new object.

**Mutable types in Python include:**
- Lists
- Dictionaries
- Sets
- User-defined classes (by default)

For example, with lists:
```python
my_list = [1, 2, 3]
my_list.append(4)  # Modifies the existing list, doesn't create a new one
```

## Key Implications

1. **Function Arguments**:
   Mutable objects passed to functions can be modified within the function, affecting the original object:

   ```python
   def add_item(my_list):
       my_list.append(4)
       
   numbers = [1, 2, 3]
   add_item(numbers)
   print(numbers)  # Output: [1, 2, 3, 4]
   ```

2. **Dictionary Keys**:
   Only immutable objects can be used as dictionary keys.

3. **Identity vs Equality**:
   Two immutable objects with the same value may share the same memory location (identity), while mutable objects with the same values are always separate objects.

4. **Default Function Arguments**:
   Using mutable objects as default arguments can lead to unexpected behavior:

   ```python
   def add_item(item, my_list=[]):  # DANGEROUS!
       my_list.append(item)
       return my_list
   ```

Understanding the distinction between mutable and immutable objects is crucial for avoiding bugs related to object references and unexpected side effects in Python.
