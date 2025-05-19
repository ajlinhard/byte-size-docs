To iterate over data returned from SQLAlchemy's `first()` and `query()` methods, you'll need to handle them differently as they return different types of results.

## Iterating over `query()` results

The `query()` method returns a Query object that is iterable:

```python
# Basic iteration over all results
users = session.query(User).all()
for user in users:
    print(user.name)

# Direct iteration without .all()
for user in session.query(User):
    print(user.name)
    
# With filtering
for user in session.query(User).filter(User.age > 21):
    print(user.name)
```

## Iterating over `first()` results

The `first()` method returns a single object or None, so you don't typically iterate over it:

```python
# first() returns a single result or None
user = session.query(User).filter(User.id == 1).first()

# Check if the result exists
if user:
    print(user.name)
    print(user.email)
    # Access other attributes
else:
    print("No user found")
```

If you need to iterate over the attributes of a single result:

```python
user = session.query(User).first()
if user:
    # Method 1: Using vars() to get all attributes as dictionary
    for attr, value in vars(user).items():
        if not attr.startswith('_'):  # Skip SQLAlchemy internal attributes
            print(f"{attr}: {value}")
            
    # Method 2: If you know the specific attributes
    for attr in ['name', 'email', 'age']:
        print(f"{attr}: {getattr(user, attr)}")
```

Would you like me to explain more about handling SQLAlchemy query results?
