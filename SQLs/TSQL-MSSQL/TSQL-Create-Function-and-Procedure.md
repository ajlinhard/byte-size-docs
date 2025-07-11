# T-SQL Create Function and Procedure
Here are the CREATE FUNCTION and CREATE PROCEDURE outlines for Microsoft SQL Server:

## CREATE FUNCTION

### Scalar Function
```sql
CREATE FUNCTION [schema.]function_name
(
    @parameter1 datatype [= default_value],
    @parameter2 datatype [= default_value],
    ...
)
RETURNS return_datatype
[WITH function_option [, ...]]
AS
BEGIN
    -- Function body
    DECLARE @variable datatype;
    
    -- Logic here
    
    RETURN @return_value;
END
```

### Table-Valued Function (Inline)
```sql
CREATE FUNCTION [schema.]function_name
(
    @parameter1 datatype,
    @parameter2 datatype,
    ...
)
RETURNS TABLE
AS
RETURN
(
    -- Single SELECT statement
    SELECT column1, column2, ...
    FROM table_name
    WHERE condition
);
```

### Table-Valued Function (Multi-Statement)
```sql
CREATE FUNCTION [schema.]function_name
(
    @parameter1 datatype,
    @parameter2 datatype,
    ...
)
RETURNS @return_table TABLE
(
    column1 datatype,
    column2 datatype,
    ...
)
AS
BEGIN
    -- Multiple statements
    INSERT INTO @return_table
    SELECT ...
    FROM ...
    WHERE ...;
    
    -- More logic if needed
    
    RETURN;
END
```

## CREATE PROCEDURE

### Basic Stored Procedure
```sql
CREATE PROCEDURE [schema.]procedure_name
(
    @parameter1 datatype [= default_value] [OUTPUT],
    @parameter2 datatype [= default_value] [OUTPUT],
    ...
)
[WITH procedure_option [, ...]]
AS
BEGIN
    -- Procedure body
    SET NOCOUNT ON; -- Optional, improves performance
    
    -- Declare variables
    DECLARE @variable datatype;
    
    -- Logic here
    SELECT ...
    FROM ...
    WHERE ...;
    
    -- Handle errors
    IF @@ERROR <> 0
    BEGIN
        -- Error handling
        RETURN -1;
    END
    
    RETURN 0; -- Success
END
```

### Procedure with Transaction Handling
```sql
CREATE PROCEDURE [schema.]procedure_name
(
    @parameter1 datatype,
    @parameter2 datatype
)
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        BEGIN TRANSACTION;
        
        -- Your operations here
        INSERT INTO ...
        UPDATE ...
        DELETE ...
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
            
        -- Handle the error
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        
        RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);
    END CATCH
END
```

## Common Options and Features

### Function Options:
- `SCHEMABINDING` - Binds function to schema objects it references
- `RETURNS NULL ON NULL INPUT` - Returns NULL if any parameter is NULL
- `CALLED ON NULL INPUT` - Executes even if parameters are NULL

### Procedure Options:
- `RECOMPILE` - Recompiles the procedure each time it's executed
- `ENCRYPTION` - Encrypts the procedure definition
- `EXECUTE AS` - Specifies security context for execution

## Example Usage

### Function Example:
```sql
CREATE FUNCTION dbo.GetEmployeeFullName
(
    @FirstName NVARCHAR(50),
    @LastName NVARCHAR(50)
)
RETURNS NVARCHAR(101)
AS
BEGIN
    RETURN @FirstName + ' ' + @LastName;
END

-- Usage
SELECT dbo.GetEmployeeFullName('John', 'Doe') AS FullName;
```

### Procedure Example:
```sql
CREATE PROCEDURE dbo.GetEmployeesByDepartment
(
    @DepartmentID INT,
    @EmployeeCount INT OUTPUT
)
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        EmployeeID,
        FirstName,
        LastName,
        HireDate
    FROM Employees
    WHERE DepartmentID = @DepartmentID;
    
    SELECT @EmployeeCount = @@ROWCOUNT;
END

-- Usage
DECLARE @Count INT;
EXEC dbo.GetEmployeesByDepartment @DepartmentID = 1, @EmployeeCount = @Count OUTPUT;
SELECT @Count AS TotalEmployees;
```

These outlines provide the foundation for creating functions and procedures in SQL Server, with flexibility to add specific business logic as needed.
