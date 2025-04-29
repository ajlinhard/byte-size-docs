# PyODBC for MS SQL Server Cheatsheet

## Installation
```python
pip install pyodbc
```

## Connection

### Basic Connection
```python
import pyodbc

# Connection string components
server = 'server_name_or_ip'
database = 'database_name'
username = 'username'
password = 'password'

# Create connection string
conn_str = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

# Establish connection
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
```

### Connection with Windows Authentication
```python
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=server_name_or_ip;'
    'DATABASE=database_name;'
    'Trusted_Connection=yes'
)
```

### Connection with Different ODBC Drivers
Common drivers:
- `{ODBC Driver 17 for SQL Server}` (recommended)
- `{ODBC Driver 13 for SQL Server}`
- `{SQL Server}`
- `{SQL Server Native Client 11.0}`

### Connection Timeout and Other Parameters
```python
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=server_name_or_ip;'
    'DATABASE=database_name;'
    'UID=username;'
    'PWD=password;'
    'Connect Timeout=30;'
    'Encrypt=yes;'
    'TrustServerCertificate=no'
)
```

### Connection with DSN
```python
conn = pyodbc.connect('DSN=YourDSNName;UID=username;PWD=password')
```

### List Available Drivers
```python
[driver for driver in pyodbc.drivers()]
```

## Basic CRUD Operations

### Create (INSERT)
```python
# Basic insert
cursor.execute(
    "INSERT INTO Employees (FirstName, LastName, Department) VALUES (?, ?, ?)",
    'John', 'Doe', 'IT'
)

# Insert with named parameters
cursor.execute(
    "INSERT INTO Employees (FirstName, LastName, Department) VALUES (?, ?, ?)",
    'Jane', 'Smith', 'HR'
)

# Insert multiple rows
employees = [
    ('Alice', 'Johnson', 'Finance'),
    ('Bob', 'Williams', 'Marketing'),
    ('Charlie', 'Brown', 'IT')
]
cursor.executemany(
    "INSERT INTO Employees (FirstName, LastName, Department) VALUES (?, ?, ?)",
    employees
)

# Commit the transaction
conn.commit()
```

### Read (SELECT)
```python
# Basic select
cursor.execute("SELECT * FROM Employees")
rows = cursor.fetchall()
for row in rows:
    print(row)

# Select specific columns
cursor.execute("SELECT FirstName, LastName FROM Employees")

# Select with WHERE clause
cursor.execute("SELECT * FROM Employees WHERE Department = ?", 'IT')

# Fetch methods
first_row = cursor.fetchone()  # Fetch the first row
five_rows = cursor.fetchmany(5)  # Fetch next 5 rows
all_rows = cursor.fetchall()  # Fetch all remaining rows
```

### Update (UPDATE)
```python
cursor.execute(
    "UPDATE Employees SET Department = ? WHERE LastName = ?",
    'Finance', 'Doe'
)
conn.commit()

# Get number of rows affected
print(f"Rows updated: {cursor.rowcount}")
```

### Delete (DELETE)
```python
cursor.execute("DELETE FROM Employees WHERE LastName = ?", 'Doe')
conn.commit()
```

## Working with Results

### Accessing Row Data
```python
# By index
cursor.execute("SELECT FirstName, LastName, Department FROM Employees")
row = cursor.fetchone()
if row:
    first_name = row[0]
    last_name = row[1]
    department = row[2]

# By column name
cursor.execute("SELECT FirstName, LastName, Department FROM Employees")
row = cursor.fetchone()
if row:
    first_name = row.FirstName
    last_name = row.LastName
    department = row.Department
```

### Row as a Dictionary
```python
def row_to_dict(cursor, row):
    return {column[0]: value for column, value in zip(cursor.description, row)}

# Set row factory
cursor.execute("SELECT * FROM Employees")
rows = cursor.fetchall()
results = [row_to_dict(cursor, row) for row in rows]
```

### Get Column Names
```python
cursor.execute("SELECT * FROM Employees")
column_names = [column[0] for column in cursor.description]
```

## Advanced Features

### Executing Stored Procedures
```python
# Basic execution
cursor.execute("{CALL dbo.GetEmployeesByDepartment(?)}", 'IT')
rows = cursor.fetchall()

# With output parameters
params = (
    'IT',                      # Input parameter
    pyodbc.SQL_VARIANT,        # Output parameter type
    pyodbc.SQL_PARAM_OUTPUT    # Parameter direction
)
cursor.execute("{CALL dbo.CountEmployeesByDepartment(?, ?)}", params)
count = params[1]  # Get output parameter value
```

### Transactions
```python
# Explicit transaction control
conn.autocommit = False  # Default is False already
try:
    cursor.execute("INSERT INTO Departments VALUES ('New Dept')")
    cursor.execute("UPDATE Employees SET Department = 'New Dept' WHERE EmployeeID = 1")
    conn.commit()
except pyodbc.Error as e:
    conn.rollback()
    print(f"Transaction failed: {e}")
```

### Batch Operations
```python
# Execute multiple statements
cursor.execute("""
    INSERT INTO Departments VALUES ('Research');
    UPDATE Employees SET Department = 'Research' WHERE EmployeeID = 2;
    SELECT * FROM Employees WHERE Department = 'Research';
""")
```

### Working with Different Data Types

#### Dates and Timestamps
```python
import datetime

# Insert date
today = datetime.date.today()
cursor.execute("INSERT INTO Events (EventDate) VALUES (?)", today)

# Insert timestamp
now = datetime.datetime.now()
cursor.execute("INSERT INTO Logs (LogTime) VALUES (?)", now)

# Format from SQL Server
cursor.execute("SELECT CAST('2023-01-15' AS DATE) AS FormattedDate")
date_value = cursor.fetchone()[0]  # Returns as Python datetime.date
```

#### Binary Data
```python
# Insert binary data
with open('image.jpg', 'rb') as f:
    binary_data = f.read()
cursor.execute("INSERT INTO Documents (DocName, DocContent) VALUES (?, ?)", 
               'image.jpg', pyodbc.Binary(binary_data))

# Retrieve binary data
cursor.execute("SELECT DocContent FROM Documents WHERE DocName = ?", 'image.jpg')
binary_data = cursor.fetchone()[0]
with open('retrieved_image.jpg', 'wb') as f:
    f.write(binary_data)
```

#### NULL Values
```python
cursor.execute("INSERT INTO Employees (FirstName, MiddleName, LastName) VALUES (?, ?, ?)",
               'John', None, 'Doe')
```

## Error Handling

### Basic Error Handling
```python
try:
    cursor.execute("INSERT INTO NonExistentTable VALUES (1)")
    conn.commit()
except pyodbc.Error as e:
    print(f"Database error: {e}")
    conn.rollback()
```

### Connection Errors
```python
try:
    conn = pyodbc.connect(conn_str)
except pyodbc.Error as e:
    print(f"Connection error: {e}")
```

### Get Detailed Error Information
```python
try:
    cursor.execute("BAD SQL STATEMENT")
except pyodbc.Error as e:
    sqlstate = e.args[0]    # SQLSTATE code
    message = e.args[1]     # Error message
    print(f"SQLSTATE: {sqlstate}, Message: {message}")
```

## Performance Tips

### Connection Pooling
```python
# Enable connection pooling (Windows only)
conn_str += ';MARS_Connection=Yes'

# To disable pooling
conn_str += ';Pooling=No'
```

### Fast Executemany
```python
# Standard executemany (slower)
cursor.executemany("INSERT INTO Table VALUES (?)", [(1,), (2,), (3,)])

# Fast executemany (faster for large datasets)
cursor.fast_executemany = True
cursor.executemany("INSERT INTO Table VALUES (?)", [(1,), (2,), (3,)])
```

### Using MARS (Multiple Active Result Sets)
```python
conn_str += ';MARS_Connection=Yes'
conn = pyodbc.connect(conn_str)

# Now you can have multiple active statements
cursor1 = conn.cursor()
cursor2 = conn.cursor()
cursor1.execute("SELECT * FROM Table1")
cursor2.execute("SELECT * FROM Table2")  # Won't block waiting for cursor1 to finish
```

## Connection Management

### Closing Resources
```python
# Always close your connections
try:
    # Use connection
    cursor.execute("SELECT * FROM Table")
    rows = cursor.fetchall()
finally:
    cursor.close()  # Close cursor
    conn.close()    # Close connection
```

### Context Manager (Recommended)
```python
# Automatically handles closing connections and transactions
with pyodbc.connect(conn_str) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM Employees")
        rows = cursor.fetchall()
    # Cursor is automatically closed here
# Connection is automatically closed here
```

## Working with Server Information

### Get Server Version
```python
cursor.execute("SELECT @@VERSION")
version = cursor.fetchone()[0]
print(version)
```

### Get Server Name
```python
cursor.execute("SELECT @@SERVERNAME")
server_name = cursor.fetchone()[0]
```

### List Databases
```python
cursor.execute("SELECT name FROM sys.databases ORDER BY name")
databases = [row[0] for row in cursor.fetchall()]
```

### List Tables in Current Database
```python
cursor.execute("""
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_NAME
""")
tables = [row[0] for row in cursor.fetchall()]
```

## Common Issues and Solutions

### Driver Not Found
```
pyodbc.Error: ('01000', "[01000] [unixODBC][Driver Manager]Can't open lib 'ODBC Driver 17 for SQL Server'")
```
Solution: Install the appropriate driver for your platform.

### Windows:
- Download and install Microsoft ODBC Driver from Microsoft's website
- Verify with `pyodbc.drivers()`

### Linux (Ubuntu/Debian):
```bash
# Install the driver
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
apt-get install -y unixodbc-dev msodbcsql17
```

### Connection Timeout
Problem: `pyodbc.OperationalError: ('08001', '[08001] [Microsoft][ODBC Driver 17 for SQL Server]TCP Provider: Timeout error [258]')`

Solution:
- Check network connectivity
- Increase timeout value: `'Connect Timeout=60'`
- Check firewall settings

### Encoding Issues
```python
# Set connection encoding
conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
conn.setencoding(encoding='utf-8')
```
