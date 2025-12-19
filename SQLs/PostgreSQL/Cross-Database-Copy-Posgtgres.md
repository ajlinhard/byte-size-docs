# Postgres Cross Database Copy
In Postgres databases wrking between 2 separate databases can be more problematic and less automatic then other SQL engines like MSQL or MongoDB. Here is how you setup a cross database connection.

```sql

-- On the target database, install the extension
CREATE EXTENSION postgres_fdw;

-- Create a server connection to the source database
CREATE SERVER source_db_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (dbname 'va_claims_tracking', port '5432');

-- Create user mapping for authentication
CREATE USER MAPPING FOR current_user
SERVER source_db_server
OPTIONS (user 'postgres', password '#Lqtq5ASr6WYA90#XQc1_r(.)nAo');

-- Create a separate schema for foreign tables
CREATE SCHEMA remote_db;

-- Import the foreign schema (or specific tables)
IMPORT FOREIGN SCHEMA public
FROM SERVER source_db_server
INTO remote_db;

select * from public.users;

insert into public.users
select *
from remote_db.users;
```
