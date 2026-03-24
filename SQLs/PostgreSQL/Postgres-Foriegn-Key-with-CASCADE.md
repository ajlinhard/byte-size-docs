# Postgres Foreign Key with CASCADE
You can use `ON UPDATE CASCADE` to automatically update the foreign key column when the referenced key changes, but there are important limitations:

## What `ON UPDATE` Can Do

```sql
CONSTRAINT contention_review_log_contention_log_id_fkey 
    FOREIGN KEY (contention_log_id)
    REFERENCES public.claim_contention (contention_log_id) 
    ON UPDATE CASCADE  -- Automatically updates this column when referenced ID changes
    ON DELETE CASCADE  -- or NO ACTION, SET NULL, etc.
```

**This will work for:**
- When `contention_log_id` in `claim_contention` table is updated, it automatically updates `contention_log_id` in your table

## What `ON UPDATE` CANNOT Do

`ON UPDATE CASCADE` **only** propagates changes to the **referenced key column itself** (the ID). It does **NOT** propagate changes to other columns in the referenced table.

If you want to update other columns based on changes in the referenced table, you need **triggers**.

## Example: Using Triggers for Other Columns

```sql
-- Create a trigger function
CREATE OR REPLACE FUNCTION update_from_claim_contention()
RETURNS TRIGGER AS $$
BEGIN
    -- Update other columns in your table when claim_contention changes
    UPDATE your_table
    SET some_column = NEW.some_column,
        another_column = NEW.another_column,
        updated_at = NOW()
    WHERE contention_log_id = NEW.contention_log_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger on claim_contention table
CREATE TRIGGER sync_contention_changes
AFTER UPDATE ON public.claim_contention
FOR EACH ROW
EXECUTE FUNCTION update_from_claim_contention();
```

## ON UPDATE Options

| Option | Behavior |
|--------|----------|
| `CASCADE` | Automatically updates the FK column |
| `NO ACTION` | Prevents update if dependent rows exist (default) |
| `RESTRICT` | Same as NO ACTION but checked immediately |
| `SET NULL` | Sets FK column to NULL |
| `SET DEFAULT` | Sets FK column to its default value |

**Which approach do you need?** Just cascading ID changes, or syncing other column values too?

---
# SQL Server Equivalent
SQL Server supports both foreign key `ON UPDATE CASCADE` and triggers, but with slightly different syntax.

## Foreign Key with ON UPDATE CASCADE

SQL Server syntax is nearly identical:

```sql
CONSTRAINT contention_review_log_contention_log_id_fkey 
    FOREIGN KEY (contention_log_id)
    REFERENCES claim_contention (contention_log_id) 
    ON UPDATE CASCADE  -- Same as PostgreSQL
    ON DELETE CASCADE  -- or NO ACTION, SET NULL, SET DEFAULT
```

## Triggers for Other Columns (T-SQL Syntax)

SQL Server uses T-SQL instead of PL/pgSQL:

```sql
CREATE TRIGGER sync_contention_changes
ON claim_contention
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Update other columns in your table when claim_contention changes
    UPDATE t
    SET t.some_column = i.some_column,
        t.another_column = i.another_column,
        t.updated_at = GETDATE()
    FROM your_table t
    INNER JOIN inserted i ON t.contention_log_id = i.contention_log_id
    -- Optional: only update if specific columns changed
    INNER JOIN deleted d ON i.contention_log_id = d.contention_log_id
    WHERE i.some_column <> d.some_column 
       OR i.another_column <> d.another_column;
END;
GO
```

## Key Differences: SQL Server vs PostgreSQL

| Feature | PostgreSQL | SQL Server |
|---------|------------|------------|
| **ON UPDATE CASCADE** | ✅ Supported | ✅ Supported (same syntax) |
| **Trigger language** | PL/pgSQL | T-SQL |
| **NEW/OLD records** | `NEW` and `OLD` | `inserted` and `deleted` tables |
| **Return value** | `RETURN NEW/OLD` | No return needed |
| **Date function** | `NOW()` | `GETDATE()` or `SYSDATETIME()` |
| **SET NOCOUNT** | Not needed | Recommended for performance |

## SQL Server Trigger Details

**Special tables in SQL Server triggers:**
- `inserted` - Contains new values (equivalent to PostgreSQL's `NEW`)
- `deleted` - Contains old values (equivalent to PostgreSQL's `OLD`)

**Example with conditional update:**

```sql
CREATE TRIGGER sync_contention_changes
ON claim_contention
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Only update if specific columns changed
    IF UPDATE(some_column) OR UPDATE(another_column)
    BEGIN
        UPDATE t
        SET t.some_column = i.some_column,
            t.another_column = i.another_column,
            t.updated_at = GETDATE()
        FROM your_table t
        INNER JOIN inserted i ON t.contention_log_id = i.contention_log_id;
    END;
END;
GO
```

The main difference is syntax - the concepts and capabilities are very similar between the two databases!
