# SQL Vocabulary

These are categories of SQL commands that serve different purposes in database management:

**DDL (Data Definition Language)**: Commands that define and modify database structure and schema.
- `CREATE` - Create tables, indexes, databases
- `ALTER` - Modify existing table structure
- `DROP` - Delete tables, indexes, databases
- `TRUNCATE` - Remove all data from a table (but keep structure)
- `COMMENT` - Add comments to schema objects

**DML (Data Manipulation Language)**: Commands that manipulate data within existing structures.
- `SELECT` - Retrieve data
- `INSERT` - Add new records
- `UPDATE` - Modify existing records
- `DELETE` - Remove specific records

**DCL (Data Control Language)**: Commands that control access and permissions.
- `GRANT` - Give permissions to users/roles
- `REVOKE` - Remove permissions from users/roles
- `DENY` - Explicitly deny permissions (some databases)

**TCL (Transaction Control Language)**: Commands that manage database transactions.
- `COMMIT` - Permanently save transaction changes
- `ROLLBACK` - Undo transaction changes
- `SAVEPOINT` - Create checkpoint within transaction
- `SET TRANSACTION` - Define transaction characteristics

**DQL (Data Query Language)**: Sometimes separated from DML, specifically for data retrieval.
- `SELECT` - Query and retrieve data (though often considered part of DML)

**Additional database-related acronyms:**

**DAL (Data Access Language)**: General term encompassing all SQL commands for accessing data.

**SCL (Session Control Language)**: Commands that manage database session properties (less commonly used category).

The most commonly used distinction is between DDL (structure changes) and DML (data changes), as these often have different permission requirements and operational impacts in production databases.
