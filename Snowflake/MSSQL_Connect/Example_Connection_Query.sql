SELECT * FROM OPENQUERY(SF_TEST, 'select top 100 * from DATABASE_NAME.PUBLIC.Example_VW')

--Not all data types translate between database engines. You need to understand the conversions a capabilities
    --Examples: In Snowflake
        -- varchar above 8000 does not translate to MS-SQL
        -- JSON or Variant has issues translating as well.
        -- integer needs to be explicitly cast, the number(38,0) does not implicitly convert over to MS-SQL
        --More Info: https://docs.snowflake.com/en/sql-reference/intro-summary-data-types
SELECT * FROM OPENQUERY(SF_TEST, 'select top 100 * from DATABASE_NAME.PUBLIC.Example_Table')