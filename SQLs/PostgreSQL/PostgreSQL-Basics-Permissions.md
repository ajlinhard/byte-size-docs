# PostgreSQL (PSQL) Command Line Cheatsheet
**Key sections include:**
- **Connection Commands** - Various ways to connect to PostgreSQL servers
- **Database Operations** - Creating, dropping, and managing databases
- **Table Operations** - Creating, modifying, and dropping tables
- **Querying and Data Operations** - SELECT, INSERT, UPDATE, DELETE operations
- **User Management** - Creating users and changing passwords
- **Permissions and Privileges** - Database, table, and schema-level permissions
- **PSQL Meta Commands** - Built-in PostgreSQL commands for information and formatting
- **Backup and Restore** - Using pg_dump and pg_restore
- **Advanced Operations** - Indexes, transactions, and system information

The cheatsheet includes practical examples for each command type and covers both basic and advanced use cases. It's formatted in a way that makes it easy to quickly find and reference specific commands when working with PostgreSQL from the command line.

## Connection Commands

### Basic Connection
```bash
# Connect to PostgreSQL
psql -U username -d database_name -h hostname -p port

# Connect to local PostgreSQL with default settings
psql

# Connect to specific database
psql database_name

# Connect with password prompt
psql -U username -W

# Connect to remote server
psql -h 192.168.1.100 -U username -d database_name
```

### Connection Examples
```bash
# Local connection as postgres user
psql -U postgres

# Remote connection with all parameters
psql -h localhost -p 5432 -U myuser -d mydb
```

## Database Operations

### Create and Drop Databases
```sql
-- Create database
CREATE DATABASE database_name;
CREATE DATABASE myapp WITH OWNER = myuser ENCODING = 'UTF8';

-- Drop database
DROP DATABASE database_name;
DROP DATABASE IF EXISTS database_name;

-- List all databases
\l
\list
```

### Database Information
```sql
-- Show current database
SELECT current_database();

-- Show database size
SELECT pg_size_pretty(pg_database_size('database_name'));

-- Switch to different database
\c database_name
\connect database_name
```

## Table Operations

### Create Tables
```sql
-- Basic table creation
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table with foreign key
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Modify Tables
```sql
-- Add column
ALTER TABLE users ADD COLUMN age INTEGER;

-- Drop column
ALTER TABLE users DROP COLUMN age;

-- Rename column
ALTER TABLE users RENAME COLUMN username TO user_name;

-- Change column type
ALTER TABLE users ALTER COLUMN age TYPE SMALLINT;

-- Add constraint
ALTER TABLE users ADD CONSTRAINT unique_email UNIQUE (email);

-- Drop constraint
ALTER TABLE users DROP CONSTRAINT unique_email;
```

### Drop Tables
```sql
-- Drop table
DROP TABLE table_name;
DROP TABLE IF EXISTS table_name;

-- Drop table with cascade
DROP TABLE table_name CASCADE;
```

## Querying and Data Operations

### Basic Queries
```sql
-- Select all
SELECT * FROM users;

-- Select specific columns
SELECT username, email FROM users;

-- With conditions
SELECT * FROM users WHERE age > 25;

-- Order results
SELECT * FROM users ORDER BY created_at DESC;

-- Limit results
SELECT * FROM users LIMIT 10 OFFSET 5;
```

### Insert Data
```sql
-- Insert single row
INSERT INTO users (username, email) VALUES ('john_doe', 'john@example.com');

-- Insert multiple rows
INSERT INTO users (username, email) VALUES 
('jane_doe', 'jane@example.com'),
('bob_smith', 'bob@example.com');

-- Insert with return
INSERT INTO users (username, email) VALUES ('alice', 'alice@example.com') RETURNING id;
```

### Update and Delete
```sql
-- Update records
UPDATE users SET email = 'newemail@example.com' WHERE username = 'john_doe';

-- Delete records
DELETE FROM users WHERE id = 1;
DELETE FROM users WHERE created_at < '2023-01-01';

-- Truncate table (delete all data)
TRUNCATE TABLE table_name;
```

## User Management

### Create and Drop Users
```sql
-- Create user
CREATE USER username WITH PASSWORD 'password';
CREATE USER myuser WITH CREATEDB PASSWORD 'mypassword';

-- Create user with specific privileges
CREATE USER admin_user WITH SUPERUSER CREATEDB CREATEROLE PASSWORD 'adminpass';

-- Drop user
DROP USER username;
DROP USER IF EXISTS username;

-- List all users
\du
```

### Change Passwords
```sql
-- Change user password
ALTER USER username WITH PASSWORD 'newpassword';

-- Change your own password
\password

-- Change specific user password (as superuser)
\password username
```

### User Properties
```sql
-- Grant/revoke superuser
ALTER USER username WITH SUPERUSER;
ALTER USER username WITH NOSUPERUSER;

-- Grant/revoke create database
ALTER USER username WITH CREATEDB;
ALTER USER username WITH NOCREATEDB;

-- Grant/revoke create role
ALTER USER username WITH CREATEROLE;
ALTER USER username WITH NOCREATEROLE;
```

## Permissions and Privileges

### Database Privileges
```sql
-- Grant database access
GRANT CONNECT ON DATABASE database_name TO username;

-- Grant all privileges on database
GRANT ALL PRIVILEGES ON DATABASE database_name TO username;

-- Revoke privileges
REVOKE CONNECT ON DATABASE database_name FROM username;
REVOKE ALL PRIVILEGES ON DATABASE database_name FROM username;
```

### Table Privileges
```sql
-- Grant table privileges
GRANT SELECT ON table_name TO username;
GRANT SELECT, INSERT, UPDATE ON table_name TO username;
GRANT ALL PRIVILEGES ON table_name TO username;

-- Grant on all tables in schema
GRANT SELECT ON ALL TABLES IN SCHEMA public TO username;

-- Grant privileges on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO username;

-- Revoke privileges
REVOKE SELECT ON table_name FROM username;
REVOKE ALL PRIVILEGES ON table_name FROM username;
```

### Schema Privileges
```sql
-- Grant schema usage
GRANT USAGE ON SCHEMA schema_name TO username;

-- Grant create in schema
GRANT CREATE ON SCHEMA schema_name TO username;

-- Grant all on schema
GRANT ALL ON SCHEMA schema_name TO username;
```

## PSQL Meta Commands

### Information Commands
```sql
-- List tables
\dt

-- List tables with sizes
\dt+

-- Describe table structure
\d table_name

-- List all schemas
\dn

-- List functions
\df

-- List views
\dv

-- List indexes
\di

-- Show table permissions
\dp table_name
\z table_name
```

### Display and Formatting
```sql
-- Toggle expanded display
\x

-- Set output format
\pset format html
\pset format csv

-- Show query execution time
\timing

-- Set null display
\pset null 'NULL'
```

### File Operations
```sql
-- Execute SQL from file
\i /path/to/file.sql

-- Save query results to file
\o /path/to/output.txt
SELECT * FROM users;
\o

-- Copy table to CSV
\copy table_name TO '/path/to/file.csv' CSV HEADER;

-- Copy from CSV to table
\copy table_name FROM '/path/to/file.csv' CSV HEADER;
```

## Backup and Restore

### pg_dump (Backup)
```bash
# Backup entire database
pg_dump database_name > backup.sql

# Backup with compression
pg_dump database_name | gzip > backup.sql.gz

# Backup specific table
pg_dump -t table_name database_name > table_backup.sql

# Custom format backup
pg_dump -Fc database_name > backup.dump
```

### pg_restore (Restore)
```bash
# Restore from SQL file
psql database_name < backup.sql

# Restore custom format
pg_restore -d database_name backup.dump

# Restore with specific options
pg_restore -d database_name --clean --if-exists backup.dump
```

## Advanced Operations

### Indexes
```sql
-- Create index
CREATE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Create partial index
CREATE INDEX idx_active_users ON users(username) WHERE active = true;

-- Drop index
DROP INDEX idx_users_email;

-- List indexes for table
\di table_name
```

### Transactions
```sql
-- Begin transaction
BEGIN;

-- Commit transaction
COMMIT;

-- Rollback transaction
ROLLBACK;

-- Savepoint
SAVEPOINT my_savepoint;
ROLLBACK TO my_savepoint;
```

### System Information
```sql
-- Show current user
SELECT current_user;

-- Show PostgreSQL version
SELECT version();

-- Show current database
SELECT current_database();

-- Show active connections
SELECT * FROM pg_stat_activity;

-- Show database sizes
SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database;
```

## Useful Tips

### Connection Shortcuts
```bash
# Set environment variables to avoid typing connection details
export PGHOST=localhost
export PGPORT=5432
export PGUSER=myuser
export PGDATABASE=mydb
```

### Quick Commands
```sql
-- Exit psql
\q

-- Clear screen
\! clear

-- Show help
\?

-- Help for SQL commands
\h CREATE TABLE

-- Edit query in external editor
\e

-- Show last executed query
\p
```

### Performance Monitoring
```sql
-- Show slow queries
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC;

-- Show table statistics
SELECT * FROM pg_stat_user_tables WHERE relname = 'table_name';
```
