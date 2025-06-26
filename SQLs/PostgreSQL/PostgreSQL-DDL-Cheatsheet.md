# PostgreSQL DDL Cheatsheet
I'll create a comprehensive PostgreSQL DDL cheatsheet for you covering psql commands, table operations, and other essential SQL actions.I've created a comprehensive PostgreSQL DDL cheatsheet that covers all the essential commands you'll need. The cheatsheet is organized into logical sections:

- **psql meta-commands** for navigation and information
- **Database operations** for creating and managing databases
- **Table operations** including CREATE, ALTER, and DROP
- **Constraints** (primary key, foreign key, unique, check)
- **Indexes** creation and management
- **Views** including materialized views
- **Sequences** for auto-incrementing values
- **Common data types** reference
- **Useful queries** for system information and maintenance

The cheatsheet includes practical examples and covers both basic and advanced operations. You can reference this when working with PostgreSQL databases, whether you're setting up new schemas, modifying existing tables, or performing maintenance tasks.

---
# PostgreSQL DDL & psql Cheatsheet

## psql Meta-Commands

### Connection & Database
```sql
\c database_name           -- Connect to database
\c database_name username  -- Connect as specific user
\l                        -- List all databases
\q                        -- Quit psql
```

### Schema & Table Information
```sql
\d                        -- List all tables, views, sequences
\dt                       -- List tables only
\dv                       -- List views only
\ds                       -- List sequences
\di                       -- List indexes
\d table_name             -- Describe table structure
\d+ table_name            -- Detailed table info with size
\dn                       -- List schemas
\df                       -- List functions
```

### Users & Permissions
```sql
\du                       -- List users and roles
\dp table_name            -- Show table permissions
\z table_name             -- Show table permissions (alternative)
```

### Output & Display
```sql
\x                        -- Toggle expanded display
\timing                   -- Toggle query timing
\pset pager off           -- Disable pager
\echo 'message'           -- Print message
```

## Database Operations

### Create & Drop Database
```sql
CREATE DATABASE database_name;
CREATE DATABASE mydb 
    WITH OWNER = username 
    ENCODING = 'UTF8' 
    LC_COLLATE = 'en_US.UTF-8';

DROP DATABASE database_name;
DROP DATABASE IF EXISTS database_name;
```

### Schemas
```sql
CREATE SCHEMA schema_name;
CREATE SCHEMA IF NOT EXISTS schema_name;
DROP SCHEMA schema_name;
DROP SCHEMA schema_name CASCADE;  -- Drop with all objects

-- Set search path
SET search_path TO schema_name, public;
```

## Table Operations

### Create Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    age INTEGER CHECK (age >= 0),
    bio TEXT,
    salary DECIMAL(10,2)
);

-- Create table from another table
CREATE TABLE users_backup AS SELECT * FROM users;
CREATE TABLE users_template (LIKE users INCLUDING ALL);
```

### Alter Table Structure
```sql
-- Add columns
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
ALTER TABLE users ADD COLUMN last_login TIMESTAMP;

-- Drop columns
ALTER TABLE users DROP COLUMN bio;
ALTER TABLE users DROP COLUMN IF EXISTS bio;

-- Rename column
ALTER TABLE users RENAME COLUMN username TO user_name;

-- Change column type
ALTER TABLE users ALTER COLUMN age TYPE BIGINT;
ALTER TABLE users ALTER COLUMN email TYPE VARCHAR(150);

-- Set/drop default values
ALTER TABLE users ALTER COLUMN is_active SET DEFAULT false;
ALTER TABLE users ALTER COLUMN is_active DROP DEFAULT;

-- Set/drop NOT NULL
ALTER TABLE users ALTER COLUMN phone SET NOT NULL;
ALTER TABLE users ALTER COLUMN phone DROP NOT NULL;

-- Rename table
ALTER TABLE users RENAME TO customers;
```

### Constraints

#### Primary Key
```sql
-- Add primary key
ALTER TABLE users ADD CONSTRAINT pk_users PRIMARY KEY (id);

-- Drop primary key
ALTER TABLE users DROP CONSTRAINT pk_users;
```

#### Foreign Key
```sql
-- Add foreign key
ALTER TABLE orders ADD CONSTRAINT fk_orders_user 
    FOREIGN KEY (user_id) REFERENCES users(id);

-- Foreign key with actions
ALTER TABLE orders ADD CONSTRAINT fk_orders_user 
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE ON UPDATE RESTRICT;

-- Drop foreign key
ALTER TABLE orders DROP CONSTRAINT fk_orders_user;
```

#### Unique Constraints
```sql
-- Add unique constraint
ALTER TABLE users ADD CONSTRAINT uk_users_email UNIQUE (email);

-- Multi-column unique
ALTER TABLE users ADD CONSTRAINT uk_users_username_email 
    UNIQUE (username, email);

-- Drop unique constraint
ALTER TABLE users DROP CONSTRAINT uk_users_email;
```

#### Check Constraints
```sql
-- Add check constraint
ALTER TABLE users ADD CONSTRAINT chk_users_age 
    CHECK (age >= 0 AND age <= 150);

-- Drop check constraint
ALTER TABLE users DROP CONSTRAINT chk_users_age;
```

### Drop Table
```sql
DROP TABLE users;
DROP TABLE IF EXISTS users;
DROP TABLE users CASCADE;  -- Drop with dependent objects
```

## Indexes

### Create Indexes
```sql
-- Basic index
CREATE INDEX idx_users_email ON users(email);

-- Unique index
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Multi-column index
CREATE INDEX idx_users_name_age ON users(username, age);

-- Partial index
CREATE INDEX idx_active_users ON users(username) WHERE is_active = true;

-- Expression index
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- B-tree index (default)
CREATE INDEX idx_users_created ON users USING btree(created_at);

-- Hash index
CREATE INDEX idx_users_id_hash ON users USING hash(id);
```

### Drop Indexes
```sql
DROP INDEX idx_users_email;
DROP INDEX IF EXISTS idx_users_email;
DROP INDEX CONCURRENTLY idx_users_email;  -- Non-blocking drop
```

## Views

### Create Views
```sql
-- Simple view
CREATE VIEW active_users AS 
SELECT id, username, email FROM users WHERE is_active = true;

-- View with joins
CREATE VIEW user_orders AS
SELECT u.username, o.order_date, o.total
FROM users u
JOIN orders o ON u.id = o.user_id;

-- Materialized view
CREATE MATERIALIZED VIEW user_stats AS
SELECT 
    COUNT(*) as total_users,
    AVG(age) as avg_age
FROM users;
```

### Alter & Drop Views
```sql
-- Replace view
CREATE OR REPLACE VIEW active_users AS 
SELECT id, username, email, created_at FROM users WHERE is_active = true;

-- Drop view
DROP VIEW active_users;
DROP VIEW IF EXISTS active_users;

-- Refresh materialized view
REFRESH MATERIALIZED VIEW user_stats;
REFRESH MATERIALIZED VIEW CONCURRENTLY user_stats;  -- If unique index exists
```

## Sequences

### Create & Manage Sequences
```sql
-- Create sequence
CREATE SEQUENCE user_id_seq START 1000 INCREMENT 1;

-- Alter sequence
ALTER SEQUENCE user_id_seq RESTART WITH 2000;
ALTER SEQUENCE user_id_seq INCREMENT BY 5;

-- Use sequence
SELECT nextval('user_id_seq');
SELECT currval('user_id_seq');
SELECT setval('user_id_seq', 5000);

-- Drop sequence
DROP SEQUENCE user_id_seq;
```

## Common Data Types

```sql
-- Numeric types
INTEGER, BIGINT, SMALLINT
DECIMAL(precision, scale), NUMERIC(precision, scale)
REAL, DOUBLE PRECISION
SERIAL, BIGSERIAL

-- Character types
CHAR(n), VARCHAR(n), TEXT

-- Date/Time types
DATE, TIME, TIMESTAMP, TIMESTAMPTZ
INTERVAL

-- Boolean
BOOLEAN

-- JSON
JSON, JSONB

-- Arrays
INTEGER[], TEXT[], VARCHAR(50)[]

-- UUID
UUID
```

## Useful Queries

### Information Schema Queries
```sql
-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Column information
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'users';

-- Index information
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'users';

-- Foreign key constraints
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = 'orders';
```

### Performance & Maintenance
```sql
-- Analyze table statistics
ANALYZE users;
ANALYZE;  -- All tables

-- Vacuum table
VACUUM users;
VACUUM FULL users;  -- Reclaim space (blocks table)
VACUUM ANALYZE users;  -- Vacuum and analyze together

-- Check table bloat
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
       pg_stat_get_live_tuples(c.oid) as live_tuples,
       pg_stat_get_dead_tuples(c.oid) as dead_tuples
FROM pg_tables t
JOIN pg_class c ON c.relname = t.tablename
WHERE schemaname = 'public';
```

## Quick Tips

- Use `\timing` to see query execution times
- Use `EXPLAIN ANALYZE` to analyze query performance
- Always backup before major DDL operations
- Use transactions for multiple DDL operations
- Consider `CONCURRENTLY` for index operations on large tables
- Use `IF EXISTS` and `IF NOT EXISTS` for safer scripts
