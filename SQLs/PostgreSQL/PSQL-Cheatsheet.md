# PSQL Cheatsheet

## PSQL Query Window Navigation
The `(END)` you're seeing means PostgreSQL is using a **pager** (usually `less`) to display the results because the output is longer than your terminal window can show at once.

## How to Navigate and Exit

When you see `(END)`:

- **Press `q`** - This is the quickest way to quit and return to the psql prompt
- **Press `Space`** - Scroll down one page
- **Press `Enter`** - Scroll down one line  
- **Press `b`** - Scroll back up one page
- **Press `g`** - Go to beginning
- **Press `G`** - Go to end
- **Press `/search_term`** - Search for text
- **Press `h`** - Show help for navigation commands

## How to Disable the Pager

If you find this annoying, you can turn off the pager:

```sql
-- Turn off pager for current session
\pset pager off

-- Turn it back on
\pset pager on

-- Check current pager setting
\pset pager
```

You can also set this permanently in your `.psqlrc` file:
```bash
# In ~/.psqlrc file
\pset pager off
```

## Alternative: Control Pager Behavior

```sql
-- Only use pager when output is longer than terminal
\pset pager always    -- Always use pager
\pset pager off       -- Never use pager  
\pset pager on        -- Use pager when needed (default)
```

## Why This Happens

The pager kicks in when:
- Query results have many rows
- Query results have wide columns
- The output would scroll past your terminal window

This is actually a helpful feature for large result sets, but can be surprising if you're not expecting it. Most people either get used to pressing `q` to exit, or turn off the pager if they prefer to see all output scroll by normally.

---
# PostgreSQL psql Commands Cheatsheet

## Connection & Basic Commands

| Command | Description |
|---------|-------------|
| `psql -d dbname -U username -h hostname` | Connect to database |
| `psql postgresql://user:pass@host:port/db` | Connect using URI |
| `\c dbname` | Connect to different database |
| `\c dbname username` | Connect to database as different user |
| `\q` | Quit psql |
| `\! command` | Execute shell command |
| `\timing` | Toggle query execution timing |

## Database Information

| Command | Description |
|---------|-------------|
| `\l` | List all databases |
| `\l+` | List databases with details |
| `\d` | List all tables, views, sequences |
| `\dt` | List tables only |
| `\dv` | List views only |
| `\di` | List indexes |
| `\ds` | List sequences |
| `\df` | List functions |
| `\dn` | List schemas |
| `\du` | List users/roles |

## Table Information

| Command | Description |
|---------|-------------|
| `\d tablename` | Describe table structure |
| `\d+ tablename` | Describe table with extra details |
| `\dt schema.*` | List tables in specific schema |
| `\d *pattern*` | List objects matching pattern |
| `\dp tablename` | Show table permissions |
| `\z tablename` | Show table permissions (same as \dp) |

## Schema & Search Path

| Command | Description |
|---------|-------------|
| `\dn` | List all schemas |
| `\dn+` | List schemas with permissions |
| `SET search_path TO schema1,schema2,public;` | Set schema search path |
| `SHOW search_path;` | Show current search path |
| `SELECT current_schema();` | Show current schema |

## Query & Output Control

| Command | Description |
|---------|-------------|
| `\pset pager off` | Turn off pager (no more END screens) |
| `\pset pager on` | Turn on pager |
| `\x` | Toggle expanded display (vertical format) |
| `\x auto` | Auto-expand when output is wide |
| `\a` | Toggle unaligned output |
| `\t` | Toggle tuple-only mode (hide headers) |
| `\H` | Toggle HTML output |
| `\copy` | Import/export data from files |

## File Operations

| Command | Description |
|---------|-------------|
| `\i filename.sql` | Execute SQL file |
| `\ir filename.sql` | Execute SQL file (relative to current file) |
| `\o filename` | Send output to file |
| `\o` | Send output back to terminal |
| `\w filename` | Write query buffer to file |
| `\copy table TO 'file.csv' CSV HEADER` | Export table to CSV |
| `\copy table FROM 'file.csv' CSV HEADER` | Import CSV to table |

## Query Buffer & History

| Command | Description |
|---------|-------------|
| `\e` | Edit query in external editor |
| `\e filename` | Edit file in external editor |
| `\p` | Show current query buffer |
| `\r` | Reset (clear) query buffer |
| `\g` | Execute current query buffer |
| `\s` | Show command history |
| `\s filename` | Save command history to file |

## Variables & Settings

| Command | Description |
|---------|-------------|
| `\set varname value` | Set variable |
| `\set` | Show all variables |
| `\unset varname` | Unset variable |
| `\echo :varname` | Display variable value |
| `\prompt 'Enter name: ' username` | Prompt for input |
| `SELECT :'varname';` | Use variable in query |

## Information & Help

| Command | Description |
|---------|-------------|
| `\?` | Show all psql commands help |
| `\h` | Show SQL commands help |
| `\h SELECT` | Show help for specific SQL command |
| `\dconfig` | Show configuration parameters |
| `\conninfo` | Show connection information |
| `SELECT version();` | Show PostgreSQL version |
| `SELECT current_user;` | Show current user |
| `SELECT current_database();` | Show current database |

## Common SQL Queries for Database Info

```sql
-- List all tables with row counts
SELECT 
    schemaname,
    tablename,
    n_tup_ins - n_tup_del as row_count
FROM pg_stat_user_tables;

-- Show table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public';

-- Show database sizes
SELECT 
    datname,
    pg_size_pretty(pg_database_size(datname)) as size
FROM pg_database;

-- Show active connections
SELECT pid, usename, application_name, state, query 
FROM pg_stat_activity;
```

## Useful Shortcuts

| Keys | Description |
|------|-------------|
| `Ctrl+C` | Cancel current query |
| `Ctrl+D` | Exit psql (same as \q) |
| `Ctrl+L` | Clear screen |
| `Up/Down arrows` | Navigate command history |
| `Tab` | Auto-complete table/column names |
| `q` | Quit pager (when seeing END) |

## Configuration File

Create `~/.psqlrc` for persistent settings:
```sql
-- Example .psqlrc file
\set QUIET 1
\pset pager off
\x auto
\set PROMPT1 '%[%033[1m%]%M %n@%/%R%[%033[0m%]%# '
\timing
\set QUIET 0
```

## Tips

- Use `\timing` to see how long queries take
- Use `\x auto` for better formatting of wide results  
- Use `\copy` instead of `COPY` for file operations (works with local files)
- Press `Tab` twice to see available completions
- Use `\d+ tablename` to see table constraints and triggers
- Use `\df+ function_name` to see function definitions
