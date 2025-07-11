# MSSQL ALTER TABLE Constraints - Concise Examples

## Primary Key Constraints

### Add Primary Key
```sql
-- Single column primary key
ALTER TABLE Users
ADD CONSTRAINT PK_Users PRIMARY KEY (UserID);

-- Composite primary key
ALTER TABLE OrderItems
ADD CONSTRAINT PK_OrderItems PRIMARY KEY (OrderID, ProductID);
```

### Drop Primary Key
```sql
ALTER TABLE Users
DROP CONSTRAINT PK_Users;
```

## Foreign Key Constraints

### Add Foreign Key
```sql
-- Basic foreign key
ALTER TABLE Orders
ADD CONSTRAINT FK_Orders_Customer 
FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID);

-- With cascading options
ALTER TABLE Orders
ADD CONSTRAINT FK_Orders_Customer 
FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
ON DELETE CASCADE ON UPDATE CASCADE;

-- Multiple foreign keys
ALTER TABLE OrderItems
ADD CONSTRAINT FK_OrderItems_Order 
FOREIGN KEY (OrderID) REFERENCES Orders(OrderID);

ALTER TABLE OrderItems
ADD CONSTRAINT FK_OrderItems_Product 
FOREIGN KEY (ProductID) REFERENCES Products(ProductID);
```

### Drop Foreign Key
```sql
ALTER TABLE Orders
DROP CONSTRAINT FK_Orders_Customer;
```

## Unique Constraints

### Add Unique Constraint
```sql
-- Single column unique
ALTER TABLE Users
ADD CONSTRAINT UQ_Users_Email UNIQUE (Email);

-- Composite unique
ALTER TABLE Employees
ADD CONSTRAINT UQ_Employees_Name UNIQUE (FirstName, LastName);
```

### Drop Unique Constraint
```sql
ALTER TABLE Users
DROP CONSTRAINT UQ_Users_Email;
```

## Check Constraints

### Add Check Constraint
```sql
-- Simple value check
ALTER TABLE Products
ADD CONSTRAINT CHK_Products_Price CHECK (Price > 0);

-- Range check
ALTER TABLE Employees
ADD CONSTRAINT CHK_Employees_Age CHECK (Age >= 18 AND Age <= 65);

-- List check
ALTER TABLE Orders
ADD CONSTRAINT CHK_Orders_Status 
CHECK (Status IN ('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled'));

-- Pattern check
ALTER TABLE Employees
ADD CONSTRAINT CHK_Employees_Email CHECK (Email LIKE '%@%.%');

-- Date comparison
ALTER TABLE Orders
ADD CONSTRAINT CHK_Orders_ShipDate CHECK (ShipDate >= OrderDate OR ShipDate IS NULL);

-- Complex check
ALTER TABLE Products
ADD CONSTRAINT CHK_Products_Discount 
CHECK ((DiscountPercent >= 0 AND DiscountPercent <= 100) OR DiscountPercent IS NULL);
```

### Drop Check Constraint
```sql
ALTER TABLE Products
DROP CONSTRAINT CHK_Products_Price;
```

## Not Null Constraints

### Add Not Null
```sql
-- First update any existing NULL values
UPDATE Users SET Email = 'unknown@example.com' WHERE Email IS NULL;

-- Then add NOT NULL constraint
ALTER TABLE Users
ALTER COLUMN Email varchar(100) NOT NULL;
```

### Remove Not Null
```sql
ALTER TABLE Users
ALTER COLUMN Email varchar(100) NULL;
```

## Default Constraints

### Add Default Constraint
```sql
-- Simple default value
ALTER TABLE Orders
ADD CONSTRAINT DF_Orders_OrderDate DEFAULT GETDATE() FOR OrderDate;

-- Default with calculation
ALTER TABLE Products
ADD CONSTRAINT DF_Products_CreatedDate DEFAULT GETDATE() FOR CreatedDate;

-- Boolean default
ALTER TABLE Users
ADD CONSTRAINT DF_Users_IsActive DEFAULT 1 FOR IsActive;

-- String default
ALTER TABLE Orders
ADD CONSTRAINT DF_Orders_Status DEFAULT 'Pending' FOR Status;
```

### Drop Default Constraint
```sql
ALTER TABLE Orders
DROP CONSTRAINT DF_Orders_OrderDate;
```

## Multiple Constraints in One Statement

### Add Multiple Constraints
```sql
-- Add multiple constraints at once
ALTER TABLE Products
ADD CONSTRAINT CHK_Products_Price CHECK (Price > 0),
    CONSTRAINT CHK_Products_Quantity CHECK (Quantity >= 0),
    CONSTRAINT UQ_Products_SKU UNIQUE (SKU);
```

## Constraint Management

### Disable/Enable Constraints
```sql
-- Disable specific constraint
ALTER TABLE Orders
NOCHECK CONSTRAINT FK_Orders_Customer;

-- Enable specific constraint
ALTER TABLE Orders
CHECK CONSTRAINT FK_Orders_Customer;

-- Disable all constraints on table
ALTER TABLE Orders
NOCHECK CONSTRAINT ALL;

-- Enable all constraints on table
ALTER TABLE Orders
CHECK CONSTRAINT ALL;
```

### Find Existing Constraints
```sql
-- List all constraints on a table
SELECT 
    CONSTRAINT_NAME,
    CONSTRAINT_TYPE,
    COLUMN_NAME
FROM INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE
WHERE TABLE_NAME = 'Orders';

-- Or using system views
SELECT 
    name AS constraint_name,
    type_desc AS constraint_type
FROM sys.objects
WHERE parent_object_id = OBJECT_ID('Orders')
AND type IN ('C', 'F', 'PK', 'UQ', 'D');
```

## Common Scenarios

### Converting Existing Table
```sql
-- Add primary key to existing table
ALTER TABLE Users
ADD CONSTRAINT PK_Users PRIMARY KEY (UserID);

-- Add foreign key relationships
ALTER TABLE Orders
ADD CONSTRAINT FK_Orders_Customer 
FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID);

-- Add data validation
ALTER TABLE Products
ADD CONSTRAINT CHK_Products_Price CHECK (Price > 0);

-- Add unique constraints
ALTER TABLE Users
ADD CONSTRAINT UQ_Users_Email UNIQUE (Email);

-- Add default values
ALTER TABLE Orders
ADD CONSTRAINT DF_Orders_OrderDate DEFAULT GETDATE() FOR OrderDate;
```

### Cleanup and Restructure
```sql
-- Remove old constraints
ALTER TABLE Orders
DROP CONSTRAINT FK_Orders_OldCustomer;

-- Add new constraints
ALTER TABLE Orders
ADD CONSTRAINT FK_Orders_Customer 
FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
ON DELETE CASCADE;
```

## Quick Reference Commands

### Add Constraints
```sql
-- Primary Key
ALTER TABLE TableName ADD CONSTRAINT PK_Name PRIMARY KEY (Column);

-- Foreign Key
ALTER TABLE TableName ADD CONSTRAINT FK_Name FOREIGN KEY (Column) REFERENCES RefTable(RefColumn);

-- Unique
ALTER TABLE TableName ADD CONSTRAINT UQ_Name UNIQUE (Column);

-- Check
ALTER TABLE TableName ADD CONSTRAINT CHK_Name CHECK (Condition);

-- Default
ALTER TABLE TableName ADD CONSTRAINT DF_Name DEFAULT Value FOR Column;

-- Not Null
ALTER TABLE TableName ALTER COLUMN ColumnName DataType NOT NULL;
```

### Drop Constraints
```sql
-- Any named constraint
ALTER TABLE TableName DROP CONSTRAINT ConstraintName;

-- Remove Not Null
ALTER TABLE TableName ALTER COLUMN ColumnName DataType NULL;
```
