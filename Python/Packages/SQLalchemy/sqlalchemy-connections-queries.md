# SQLAlchemy Connection & Query Cheatsheet

## Establishing Connections

### Connection Basics

```python
from sqlalchemy import create_engine

# Basic connection formats
sqlite_engine = create_engine('sqlite:///database.db')
postgres_engine = create_engine('postgresql://username:password@hostname:port/dbname')
mysql_engine = create_engine('mysql+pymysql://username:password@hostname:port/dbname')
oracle_engine = create_engine('oracle+cx_oracle://username:password@hostname:port/service_name')
mssql_engine = create_engine('mssql+pyodbc://username:password@hostname:port/dbname?driver=ODBC+Driver+17+for+SQL+Server')
```

### Connection Options

```python
# Connection pooling options
engine = create_engine(
    'postgresql://user:pass@localhost/dbname',
    pool_size=5,               # Number of connections to keep open
    max_overflow=10,           # Max extra connections when pool is fully used
    pool_timeout=30,           # Seconds to wait before timeout on connection pool
    pool_recycle=1800,         # Recycle connections after this many seconds
    pool_pre_ping=True         # Test connections with a ping before using
)

# Echo SQL statements for debugging
engine = create_engine('sqlite:///database.db', echo=True)

# Connect with SSL/TLS
engine = create_engine(
    'postgresql://user:pass@localhost/dbname',
    connect_args={
        'sslmode': 'require',
        'sslcert': '/path/to/cert.pem',
        'sslkey': '/path/to/key.pem',
        'sslrootcert': '/path/to/ca.pem'
    }
)

# Raw connection access
connection = engine.raw_connection()
```

### Connection URL Configuration

```python
# Using URL object for more flexibility
from sqlalchemy.engine.url import URL

connection_url = URL.create(
    drivername="postgresql",
    username="user",
    password="password",
    host="localhost", 
    port=5432,
    database="dbname",
    query={"sslmode": "require"}
)

engine = create_engine(connection_url)
```

## Session Management

### Creating Sessions

```python
from sqlalchemy.orm import sessionmaker, Session

# Classic pattern
Session = sessionmaker(bind=engine)
session = Session()

# Context manager pattern (recommended)
with Session(engine) as session:
    # Work with session here
    # Auto-closes when block exits
    pass

# Scoped session for thread safety
from sqlalchemy.orm import scoped_session

Session = scoped_session(sessionmaker(bind=engine))
session = Session()
# Use session...
Session.remove()  # Clear at end of web request
```

### Session Operations

```python
# Commit changes
session.commit()

# Rollback on error
try:
    # Do work...
    session.commit()
except:
    session.rollback()
    raise
finally:
    session.close()

# Expunge object from session (detach without discarding changes)
session.expunge(user)

# Expunge all
session.expunge_all()

# Refresh object from database
session.refresh(user)

# Merge detached instance back into session
merged_user = session.merge(detached_user)

# Flush (send to DB but don't commit)
session.flush()

# Check pending changes
session.dirty    # Modified objects
session.new      # New objects pending
session.deleted  # Deleted objects pending
```

### Transaction Management

```python
# Explicit savepoints
savepoint = session.begin_nested()
try:
    # Perform operations
    savepoint.commit()
except:
    savepoint.rollback()

# Using transactions explicitly
with session.begin():
    # Operations automatically committed or rolled back
    pass

# Controlling autocommit and isolation level
engine = create_engine(
    'postgresql://user:pass@localhost/dbname',
    isolation_level='REPEATABLE READ'  # Options: SERIALIZABLE, REPEATABLE READ, READ COMMITTED, etc.
)
```

## Querying Data

### Basic Queries

```python
from sqlalchemy import select

# SQLAlchemy 2.0 style
stmt = select(User)
result = session.execute(stmt)
users = result.scalars().all()

# Legacy 1.x style
users = session.query(User).all()

# Get single item by primary key
user = session.get(User, 1)                      # 2.0 style
user = session.query(User).get(1)                # 1.x style

# First result or None
user = session.execute(select(User)).scalar_one_or_none()  # 2.0
user = session.query(User).first()                         # 1.x

# Exactly one result (raises exception if not exactly one)
user = session.execute(select(User).filter_by(id=1)).scalar_one()  # 2.0
user = session.query(User).filter_by(id=1).one()                   # 1.x

# Filtering
stmt = select(User).where(User.name == 'John')             # 2.0
users = session.query(User).filter(User.name == 'John')    # 1.x

# Filter by keyword args
stmt = select(User).filter_by(name='John', active=True)    # 2.0
users = session.query(User).filter_by(name='John')         # 1.x
```

### Advanced Filtering

```python
from sqlalchemy import and_, or_, not_, func, text

# Complex conditions
stmt = select(User).where(
    and_(
        User.age > 25,
        or_(
            User.name.like('J%'),
            User.name.like('B%')
        ),
        not_(User.status == 'inactive')
    )
)

# IN condition
stmt = select(User).where(User.id.in_([1, 2, 3]))
stmt = select(User).where(User.id.in_(
    select(Order.user_id).where(Order.amount > 100)
))

# NOT IN
stmt = select(User).where(User.id.not_in_([1, 2, 3]))

# IS NULL / IS NOT NULL
stmt = select(User).where(User.email == None)  # IS NULL
stmt = select(User).where(User.email != None)  # IS NOT NULL

# BETWEEN
stmt = select(User).where(User.age.between(18, 65))

# String comparisons
stmt = select(User).where(User.name.like('%Smith%'))       # LIKE
stmt = select(User).where(User.name.ilike('%smith%'))      # ILIKE (case insensitive)
stmt = select(User).where(User.name.startswith('J'))       # LIKE 'J%' 
stmt = select(User).where(User.name.endswith('son'))       # LIKE '%son'
stmt = select(User).where(User.name.contains('oh'))        # LIKE '%oh%'

# Ordering
stmt = select(User).order_by(User.created_at.desc(), User.name)

# Limiting & offsetting
stmt = select(User).limit(10).offset(20)

# Raw SQL in filters
stmt = select(User).where(text("users.account_balance > 1000"))
```

### Joining Tables

```python
# Basic joins
stmt = select(User, Address).join(Address)                              # 2.0
users_addresses = session.query(User, Address).join(Address).all()      # 1.x

# Join with ON condition
stmt = select(User, Address).join(Address, User.id == Address.user_id)

# Left outer join
stmt = select(User, Address).outerjoin(Address)

# Multiple joins
stmt = (
    select(User, Order, Product)
    .join(Order, User.id == Order.user_id)
    .join(Product, Order.product_id == Product.id)
)

# Join with filter
stmt = (
    select(User, Address)
    .join(Address)
    .where(Address.city == 'New York')
)

# Join to itself (self-join)
managers = aliased(Employee, name='managers')
stmt = (
    select(Employee, managers)
    .join(managers, Employee.manager_id == managers.id)
)

# Many-to-many join through association table
stmt = (
    select(Student, Course)
    .join(student_course, Student.id == student_course.c.student_id)
    .join(Course, Course.id == student_course.c.course_id)
)

# Using relationships
stmt = select(User, Address).join(User.addresses)   # Join through relationship

# Specific join types
stmt = select(User, Address).join(Address, isouter=True)  # LEFT OUTER JOIN
stmt = select(User, Address).join(Address, full=True)     # FULL OUTER JOIN
```

### Working with Results

```python
# Executing and getting results
stmt = select(User)
result = session.execute(stmt)

# Different ways to get results from 2.0 Result object
first_user = result.scalars().first()          # First item or None (scalar for first column)
all_users = result.scalars().all()             # List of all items (scalar for first column) 
user = result.scalar_one()                     # Single item (exception if not exactly one)
user = result.scalar_one_or_none()             # Single item or None
user_tuples = result.all()                     # List of tuples for all columns

# Working with multi-column results
stmt = select(User.id, User.name)
result = session.execute(stmt)
for user_id, user_name in result:              # Automatic tuple unpacking
    print(f"{user_id}: {user_name}")

# Converting results to dictionaries
stmt = select(User)
result = session.execute(stmt)
users_as_dicts = [
    {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }
    for user in result.scalars()
]

# Mapping results with column labels
stmt = select(
    User.id,
    User.name.label('full_name'),
    func.count(Order.id).label('order_count')
).join(Order).group_by(User.id, User.name)

result = session.execute(stmt)
for row in result:
    print(f"{row.id}, {row.full_name}, {row.order_count}")

# Row-to-dict conversion helper
def row2dict(row):
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}

# Using ORM entities with relationships
users = session.query(User).options(
    joinedload(User.addresses),
    joinedload(User.orders)
).all()

for user in users:
    print(f"User: {user.name}")
    for address in user.addresses:
        print(f"  Address: {address.city}")
    for order in user.orders:
        print(f"  Order: {order.amount}")
```

### Aggregation and Grouping

```python
from sqlalchemy import func, distinct, desc, asc

# Count
count = session.execute(select(func.count(User.id))).scalar_one()

# Count distinct
count = session.execute(select(func.count(distinct(User.name)))).scalar_one()

# Sum, Avg, Min, Max
total = session.execute(select(func.sum(Order.amount))).scalar_one()
avg = session.execute(select(func.avg(Order.amount))).scalar_one()
min_amount = session.execute(select(func.min(Order.amount))).scalar_one()
max_amount = session.execute(select(func.max(Order.amount))).scalar_one()

# Group by with aggregation
stmt = (
    select(
        User.country,
        func.count(User.id).label('user_count'),
        func.avg(User.age).label('avg_age')
    )
    .group_by(User.country)
    .order_by(desc('user_count'))
)
result = session.execute(stmt)
for country, count, avg_age in result:
    print(f"{country}: {count} users, avg age: {avg_age:.1f}")

# Having clause (filter on aggregated results)
stmt = (
    select(
        User.country,
        func.count(User.id).label('user_count')
    )
    .group_by(User.country)
    .having(func.count(User.id) > 10)
)

# Subqueries
subq = (
    select(
        Order.user_id,
        func.sum(Order.amount).label('total_spent')
    )
    .group_by(Order.user_id)
    .subquery()
)

stmt = (
    select(User, subq.c.total_spent)
    .join(subq, User.id == subq.c.user_id)
    .order_by(desc(subq.c.total_spent))
)
```

### Loading Related Objects

```python
from sqlalchemy.orm import joinedload, selectinload, subqueryload, lazyload, immediateload, contains_eager

# Common loading strategies
users = session.execute(
    select(User).options(joinedload(User.addresses))
).scalars().all()

# Different loading strategies
stmt = select(User).options(
    joinedload(User.addresses),       # Eager load with JOIN
    selectinload(User.orders),        # Eager load with SELECT IN
    subqueryload(User.roles),         # Eager load with subquery
    lazyload(User.preferences),       # Lazy load (default)
    immediateload(User.settings)      # Load immediately with separate queries
)

# Deep relationship loading
stmt = select(User).options(
    joinedload(User.addresses),
    selectinload(User.orders).selectinload(Order.items).selectinload(Item.details)
)

# Load specific columns only
from sqlalchemy.orm import load_only, defer, undefer
stmt = select(User).options(
    load_only(User.id, User.name, User.email),  # Load only these columns
    defer(User.created_at),                     # Defer loading this column
    joinedload(User.addresses).load_only(       # Load only specific columns from relationship
        Address.id, Address.street
    )
)

# Contains eager (use with explicit join)
stmt = (
    select(User)
    .join(User.addresses)
    .options(contains_eager(User.addresses))
    .where(Address.city == 'New York')
)
```

### Common Query Recipes

```python
# Querying with column selection
stmt = select(User.id, User.name, Address.email)

# Distinct query
stmt = select(distinct(User.country))

# Union queries
stmt = union(
    select(User.id, User.name).where(User.country == 'US'),
    select(User.id, User.name).where(User.country == 'CA')
)

# If exists
from sqlalchemy import exists
stmt = select(exists().where(User.name == 'John'))
exists_john = session.execute(stmt).scalar_one()

# Using exists in a where clause
stmt = select(User).where(
    exists(select(1).where(Address.user_id == User.id))
)
users_with_addresses = session.execute(stmt).scalars().all()

# Correlated subquery
users_stmt = select(User.id, User.name).subquery()
stmt = select(
    users_stmt.c.id,
    users_stmt.c.name,
    select(func.count(Order.id))
    .where(Order.user_id == users_stmt.c.id)
    .scalar_subquery()
    .label('order_count')
)

# Case expression
from sqlalchemy import case
stmt = select(
    User.name,
    case(
        (User.age < 18, 'Minor'),
        (User.age < 65, 'Adult'),
        else_='Senior'
    ).label('age_category')
)

# Using aliased tables
from sqlalchemy.orm import aliased
user_alias = aliased(User, name='user_alias')
stmt = select(User, user_alias).join(
    user_alias, User.manager_id == user_alias.id
)

# NULLS FIRST/LAST in order by
stmt = select(User).order_by(User.last_login.desc().nulls_last())

# Inserting query results
stmt = insert(UserArchive).from_select(
    ['id', 'name', 'email'],
    select(User.id, User.name, User.email).where(User.is_deleted == True)
)
```

## Working With Connections Directly

### Core-Level (SQL Expression) Execution

```python
# Execute SQL directly with engine (auto-commits)
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 1})
    for row in result:
        print(row)

# Core API execution
from sqlalchemy import text, select

with engine.connect() as conn:
    # Text SQL
    result = conn.execute(text("SELECT * FROM users"))
    
    # SQL Expression Language
    stmt = select(user_table).where(user_table.c.id > 5)
    result = conn.execute(stmt)
    
    # Process results
    for row in result:
        print(row)  # Row object (tuple-like)
        print(row[0])  # Access by index
        print(row.id)  # Access by name

# Transactions with engine
with engine.begin() as conn:
    # Automatically commits if no exceptions or rolls back
    conn.execute(text("UPDATE users SET status = 'active' WHERE id = :id"), {"id": 1})
```

### Fetching Data with Core

```python
with engine.connect() as conn:
    result = conn.execute(select(user_table))
    
    # Different result methods (Core)
    first_row = result.first()              # First row or None
    all_rows = result.all()                 # List of all remaining rows
    one_row = result.one()                  # One row (raises if not exactly one)
    one_or_none = result.one_or_none()      # One row or None
    
    # Mapping results to dictionaries
    result = conn.execute(select(user_table))
    dict_result = [dict(row) for row in result]  # List of dictionaries
```

### Executing Multiple Statements

```python
with engine.begin() as conn:
    # Execute multiple statements in one batch
    conn.execute(
        insert(users),
        [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"},
            {"name": "Charlie", "email": "charlie@example.com"}
        ]
    )
    
    # Executemany for bulk operations
    conn.executemany(
        text("INSERT INTO users(name, email) VALUES(:name, :email)"),
        [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"}
        ]
    )
```

### Transaction Management with Core

```python
# Managing savepoints
with engine.begin() as conn:
    savepoint = conn.begin_nested()
    try:
        conn.execute(text("UPDATE users SET credits = credits - 100 WHERE id = 1"))
        # More operations...
        savepoint.commit()
    except:
        savepoint.rollback()
        # Handle error...
        
# Connection isolation level
with engine.connect().execution_options(
    isolation_level="SERIALIZABLE"
) as conn:
    with conn.begin():
        # Execute in SERIALIZABLE isolation level
        pass
```

### Executing Raw SQL

```python
# Parameterized SQL with named parameters
with engine.connect() as conn:
    result = conn.execute(
        text("SELECT * FROM users WHERE name = :name AND age > :age"),
        {"name": "John", "age": 25}
    )
    
# Parameterized SQL with positional parameters
with engine.connect() as conn:
    result = conn.execute(
        text("SELECT * FROM users WHERE name = ? AND age > ?"),
        "John", 25
    )
    
# Multiple statements with RETURNING clause (PostgreSQL, SQLite 3.35+)
with engine.begin() as conn:
    result = conn.execute(
        text("INSERT INTO users(name, email) VALUES(:name, :email) RETURNING id"),
        {"name": "New User", "email": "new@example.com"}
    )
    new_id = result.scalar_one()  # Get the returned ID
```

## Performance Tips

```python
# Bulk operations (much faster than individual operations)
from sqlalchemy import insert, update, delete

# Bulk insert
stmt = insert(User).values([
    {"name": "User1", "email": "user1@example.com"},
    {"name": "User2", "email": "user2@example.com"},
    # ...more rows
])
session.execute(stmt)

# Bulk update 
stmt = update(User).where(User.active == False).values(status="inactive")
session.execute(stmt)

# Bulk delete
stmt = delete(User).where(User.active == False)
session.execute(stmt)

# Optimizing relationship loading
users = session.execute(
    select(User)
    .options(
        selectinload(User.addresses),  # Best for many child rows
        joinedload(User.profile)       # Best for one-to-one
    )
).scalars().all()

# Limit columns for large tables
stmt = select(
    User.id, 
    User.name
    # Omit other columns to reduce memory usage
)

# Use yield_per for large result sets
stmt = select(User)
for chunk in session.execute(stmt).scalars().yield_per(100):
    # Process 100 users at a time
    process_user(chunk)
```
