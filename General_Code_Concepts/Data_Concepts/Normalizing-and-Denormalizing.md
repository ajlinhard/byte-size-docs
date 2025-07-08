# What is Normalizing and Denormalizing Data
**Normalization** is the process of organizing data to reduce redundancy and improve data integrity by breaking it into separate, related tables. 

**Denormalization** is the opposite - combining data from multiple tables into fewer tables to improve query performance, often at the cost of some redundancy.

## Normalization Example

Here's customer and order data in normalized form (3rd Normal Form):

**Customers Table:**
```
customer_id | name          | email                | city
1          | John Smith    | john@email.com       | New York
2          | Jane Doe      | jane@email.com       | Boston
3          | Bob Johnson   | bob@email.com        | Chicago
```

**Orders Table:**
```
order_id | customer_id | order_date | total_amount
101      | 1          | 2024-01-15 | 150.00
102      | 1          | 2024-01-20 | 75.50
103      | 2          | 2024-01-18 | 200.00
104      | 3          | 2024-01-22 | 125.75
```

**Order_Items Table:**
```
item_id | order_id | product_name | quantity | price
1       | 101      | Widget A     | 2        | 25.00
2       | 101      | Widget B     | 1        | 100.00
3       | 102      | Widget A     | 1        | 25.00
4       | 102      | Widget C     | 1        | 50.50
```

## Denormalization Example

The same data denormalized into a single table:

**Order_Details Table:**
```
order_id | customer_name | customer_email   | customer_city | order_date | product_name | quantity | price | total_amount
101      | John Smith    | john@email.com   | New York     | 2024-01-15 | Widget A     | 2        | 25.00 | 150.00
101      | John Smith    | john@email.com   | New York     | 2024-01-15 | Widget B     | 1        | 100.00| 150.00
102      | John Smith    | john@email.com   | New York     | 2024-01-20 | Widget A     | 1        | 25.00 | 75.50
102      | John Smith    | john@email.com   | New York     | 2024-01-20 | Widget C     | 1        | 50.50 | 75.50
103      | Jane Doe      | jane@email.com   | Boston       | 2024-01-18 | Widget D     | 1        | 200.00| 200.00
104      | Bob Johnson   | bob@email.com    | Chicago      | 2024-01-22 | Widget E     | 3        | 41.92 | 125.75
```

## Key Differences

**Normalization advantages:**
- No data redundancy (customer info stored once)
- Better data integrity (update customer email in one place)
- Smaller storage footprint
- Easier to maintain consistency

**Denormalization advantages:**
- Faster queries (no joins needed)
- Simpler queries for reporting
- Better for read-heavy workloads
- Reduced complexity for analytics

**Normalization disadvantages:**
- Complex queries requiring multiple joins
- Slower query performance
- More complex application logic

**Denormalization disadvantages:**
- Data redundancy (John Smith's info repeated)
- Update anomalies (must update customer info in multiple rows)
- Larger storage requirements
- Risk of data inconsistency

In practice, data engineers often use normalized structures for transactional systems (OLTP) and denormalized structures for analytical systems (OLAP) and data warehouses.
