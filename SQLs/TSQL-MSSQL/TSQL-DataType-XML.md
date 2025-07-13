SQL Server provides several ways to work with XML data, depending on your needs:

## XML Data Type
SQL Server has a native `XML` data type for storing XML documents:

```sql
-- Create table with XML column
CREATE TABLE Documents (
    ID int PRIMARY KEY,
    XMLData XML
);

-- Insert XML data
INSERT INTO Documents (ID, XMLData) 
VALUES (1, '<root><item>value</item></root>');
```

## Querying XML Data
Use XQuery methods to extract data from XML columns:

```sql
-- Extract specific values
SELECT XMLData.value('(/root/item)[1]', 'varchar(50)') AS ItemValue
FROM Documents;

-- Check if nodes exist
SELECT * FROM Documents 
WHERE XMLData.exist('/root/item') = 1;

-- Extract multiple nodes
SELECT 
    T.Item.value('.', 'varchar(50)') AS ItemValue
FROM Documents
CROSS APPLY XMLData.nodes('/root/item') AS T(Item);
```

## Common XML Methods
- `.value()` - Extract a single scalar value
- `.query()` - Return XML fragments
- `.exist()` - Check if nodes exist (returns 1/0)
- `.nodes()` - Shred XML into relational format
- `.modify()` - Update XML content

## Converting Between XML and Relational Data
```sql
-- Convert query results to XML
SELECT ID, Name
FROM Employees
FOR XML AUTO;

-- Parse XML into table format
DECLARE @xml XML = '<items><item>A</item><item>B</item></items>';
SELECT 
    T.Item.value('.', 'varchar(10)') AS Value
FROM @xml.nodes('/items/item') AS T(Item);
```

## XML Indexes
For better performance on large XML columns:
```sql
CREATE PRIMARY XML INDEX IX_XMLData ON Documents(XMLData);
```

What specific XML operations are you trying to perform? I can provide more targeted examples based on your use case.
