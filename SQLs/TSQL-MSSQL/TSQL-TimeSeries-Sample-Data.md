# T-SQL TimeSeries Sample Data
I'll create sample timeseries data that you can use for T-SQL testing. This will include a variety of realistic scenarios for time-based analysis.I've created comprehensive T-SQL timeseries test data with 5 different datasets that cover common real-world scenarios:

**1. Sales Data** - Daily sales data with seasonal patterns over 2 years
**2. Server Metrics** - Hourly CPU/memory usage for 30 days 
**3. Stock Prices** - Minute-by-minute trading data for 5 business days
**4. IoT Sensor Data** - Temperature/humidity readings every 5 minutes for 7 days
**5. Web Analytics** - Hourly page view data for 14 days

The sample includes realistic data patterns like:
- Seasonal variations using SIN/COS functions
- Random variations with controlled ranges
- Different time granularities (minutes, hours, days)
- Missing weekend data for stock prices
- Multiple series per table (different products, servers, etc.)

I've also included sample queries demonstrating common timeseries operations:
- Moving averages using window functions
- Time-based aggregations with LAG/LEAD
- Gap detection for missing data
- Seasonal pattern analysis

This should give you a solid foundation for testing various T-SQL timeseries scenarios like trend analysis, forecasting, anomaly detection, and time-based reporting.

---
# Code
```sql
-- T-SQL Timeseries Test Data
-- This script creates sample tables with various timeseries patterns for testing

-- 1. Sales Data - Daily sales with seasonal patterns
CREATE TABLE SalesData (
    SaleDate DATE,
    ProductID INT,
    SalesAmount DECIMAL(10,2),
    Quantity INT,
    Region VARCHAR(50)
);

-- Insert sample sales data (2 years of data)
WITH DateSeries AS (
    SELECT CAST('2023-01-01' AS DATE) AS SaleDate
    UNION ALL
    SELECT DATEADD(DAY, 1, SaleDate)
    FROM DateSeries
    WHERE SaleDate < '2024-12-31'
)
INSERT INTO SalesData (SaleDate, ProductID, SalesAmount, Quantity, Region)
SELECT 
    d.SaleDate,
    (ABS(CHECKSUM(NEWID())) % 5) + 1 AS ProductID,
    ROUND(1000 + (500 * SIN(DATEPART(DAYOFYEAR, d.SaleDate) * 2 * PI() / 365)) + (ABS(CHECKSUM(NEWID())) % 500), 2) AS SalesAmount,
    10 + (ABS(CHECKSUM(NEWID())) % 20) AS Quantity,
    CASE (ABS(CHECKSUM(NEWID())) % 4)
        WHEN 0 THEN 'North'
        WHEN 1 THEN 'South'
        WHEN 2 THEN 'East'
        ELSE 'West'
    END AS Region
FROM DateSeries d
OPTION (MAXRECURSION 0);

-- 2. Server Metrics - Hourly CPU and Memory usage
CREATE TABLE ServerMetrics (
    Timestamp DATETIME2,
    ServerName VARCHAR(50),
    CPUUsage DECIMAL(5,2),
    MemoryUsage DECIMAL(5,2),
    DiskIO INT
);

-- Insert hourly server metrics for last 30 days
WITH HourSeries AS (
    SELECT CAST('2025-06-08 00:00:00' AS DATETIME2) AS Timestamp
    UNION ALL
    SELECT DATEADD(HOUR, 1, Timestamp)
    FROM HourSeries
    WHERE Timestamp < '2025-07-08 00:00:00'
)
INSERT INTO ServerMetrics (Timestamp, ServerName, CPUUsage, MemoryUsage, DiskIO)
SELECT 
    h.Timestamp,
    'SERVER-' + CAST((ABS(CHECKSUM(NEWID())) % 3) + 1 AS VARCHAR(1)) AS ServerName,
    ROUND(20 + (30 * SIN(DATEPART(HOUR, h.Timestamp) * PI() / 12)) + (ABS(CHECKSUM(NEWID())) % 20), 2) AS CPUUsage,
    ROUND(40 + (20 * COS(DATEPART(HOUR, h.Timestamp) * PI() / 12)) + (ABS(CHECKSUM(NEWID())) % 15), 2) AS MemoryUsage,
    100 + (ABS(CHECKSUM(NEWID())) % 200) AS DiskIO
FROM HourSeries h
OPTION (MAXRECURSION 0);

-- 3. Stock Prices - Minute-by-minute stock data
CREATE TABLE StockPrices (
    Timestamp DATETIME2,
    Symbol VARCHAR(10),
    OpenPrice DECIMAL(10,4),
    ClosePrice DECIMAL(10,4),
    HighPrice DECIMAL(10,4),
    LowPrice DECIMAL(10,4),
    Volume BIGINT
);

-- Insert stock price data for last 5 trading days (9 AM to 4 PM)
DECLARE @StartDate DATE = '2025-07-01';
DECLARE @EndDate DATE = '2025-07-07';

WITH TradingMinutes AS (
    SELECT 
        CAST(@StartDate AS DATETIME2) + CAST('09:00:00' AS TIME) AS Timestamp,
        @StartDate AS TradeDate
    UNION ALL
    SELECT 
        CASE 
            WHEN DATEADD(MINUTE, 1, Timestamp) > CAST(TradeDate AS DATETIME2) + CAST('16:00:00' AS TIME)
            THEN CAST(DATEADD(DAY, 1, TradeDate) AS DATETIME2) + CAST('09:00:00' AS TIME)
            ELSE DATEADD(MINUTE, 1, Timestamp)
        END,
        CASE 
            WHEN DATEADD(MINUTE, 1, Timestamp) > CAST(TradeDate AS DATETIME2) + CAST('16:00:00' AS TIME)
            THEN DATEADD(DAY, 1, TradeDate)
            ELSE TradeDate
        END
    FROM TradingMinutes
    WHERE TradeDate < @EndDate
        AND DATEPART(WEEKDAY, TradeDate) NOT IN (1, 7) -- Exclude weekends
)
INSERT INTO StockPrices (Timestamp, Symbol, OpenPrice, ClosePrice, HighPrice, LowPrice, Volume)
SELECT 
    t.Timestamp,
    CASE (ABS(CHECKSUM(NEWID())) % 3)
        WHEN 0 THEN 'AAPL'
        WHEN 1 THEN 'GOOGL'
        ELSE 'MSFT'
    END AS Symbol,
    ROUND(100 + (ABS(CHECKSUM(NEWID())) % 50) + (0.01 * ABS(CHECKSUM(NEWID())) % 100), 4) AS OpenPrice,
    ROUND(100 + (ABS(CHECKSUM(NEWID())) % 50) + (0.01 * ABS(CHECKSUM(NEWID())) % 100), 4) AS ClosePrice,
    ROUND(100 + (ABS(CHECKSUM(NEWID())) % 50) + (0.01 * ABS(CHECKSUM(NEWID())) % 100), 4) AS HighPrice,
    ROUND(100 + (ABS(CHECKSUM(NEWID())) % 50) + (0.01 * ABS(CHECKSUM(NEWID())) % 100), 4) AS LowPrice,
    (ABS(CHECKSUM(NEWID())) % 100000) + 1000 AS Volume
FROM TradingMinutes t
WHERE DATEPART(WEEKDAY, t.TradeDate) NOT IN (1, 7)
OPTION (MAXRECURSION 0);

-- 4. IoT Sensor Data - Temperature readings every 5 minutes
CREATE TABLE IoTSensorData (
    Timestamp DATETIME2,
    SensorID VARCHAR(20),
    Temperature DECIMAL(5,2),
    Humidity DECIMAL(5,2),
    Pressure DECIMAL(7,2),
    Location VARCHAR(100)
);

-- Insert IoT sensor data for last 7 days
WITH SensorReadings AS (
    SELECT CAST('2025-07-01 00:00:00' AS DATETIME2) AS Timestamp
    UNION ALL
    SELECT DATEADD(MINUTE, 5, Timestamp)
    FROM SensorReadings
    WHERE Timestamp < '2025-07-08 00:00:00'
)
INSERT INTO IoTSensorData (Timestamp, SensorID, Temperature, Humidity, Pressure, Location)
SELECT 
    s.Timestamp,
    'SENSOR-' + RIGHT('000' + CAST((ABS(CHECKSUM(NEWID())) % 10) + 1 AS VARCHAR(3)), 3) AS SensorID,
    ROUND(20 + (10 * SIN(DATEPART(HOUR, s.Timestamp) * PI() / 12)) + (ABS(CHECKSUM(NEWID())) % 10), 2) AS Temperature,
    ROUND(45 + (ABS(CHECKSUM(NEWID())) % 30), 2) AS Humidity,
    ROUND(1013.25 + (ABS(CHECKSUM(NEWID())) % 20) - 10, 2) AS Pressure,
    CASE (ABS(CHECKSUM(NEWID())) % 5)
        WHEN 0 THEN 'Warehouse A'
        WHEN 1 THEN 'Warehouse B'
        WHEN 2 THEN 'Office Building'
        WHEN 3 THEN 'Data Center'
        ELSE 'Manufacturing Floor'
    END AS Location
FROM SensorReadings s
OPTION (MAXRECURSION 0);

-- 5. Website Analytics - Page views by hour
CREATE TABLE WebAnalytics (
    Timestamp DATETIME2,
    PageURL VARCHAR(200),
    PageViews INT,
    UniqueVisitors INT,
    BounceRate DECIMAL(5,2),
    AvgSessionDuration INT -- in seconds
);

-- Insert web analytics data for last 14 days
WITH WebHours AS (
    SELECT CAST('2025-06-24 00:00:00' AS DATETIME2) AS Timestamp
    UNION ALL
    SELECT DATEADD(HOUR, 1, Timestamp)
    FROM WebHours
    WHERE Timestamp < '2025-07-08 00:00:00'
)
INSERT INTO WebAnalytics (Timestamp, PageURL, PageViews, UniqueVisitors, BounceRate, AvgSessionDuration)
SELECT 
    w.Timestamp,
    CASE (ABS(CHECKSUM(NEWID())) % 6)
        WHEN 0 THEN '/home'
        WHEN 1 THEN '/products'
        WHEN 2 THEN '/about'
        WHEN 3 THEN '/contact'
        WHEN 4 THEN '/blog'
        ELSE '/support'
    END AS PageURL,
    10 + (ABS(CHECKSUM(NEWID())) % 190) AS PageViews,
    5 + (ABS(CHECKSUM(NEWID())) % 95) AS UniqueVisitors,
    ROUND(20 + (ABS(CHECKSUM(NEWID())) % 60), 2) AS BounceRate,
    60 + (ABS(CHECKSUM(NEWID())) % 300) AS AvgSessionDuration
FROM WebHours w
OPTION (MAXRECURSION 0);

-- Sample queries to test timeseries functionality

-- 1. Moving average of sales
SELECT 
    SaleDate,
    SalesAmount,
    AVG(SalesAmount) OVER (
        ORDER BY SaleDate 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS MovingAvg7Days
FROM SalesData
WHERE ProductID = 1
ORDER BY SaleDate;

-- 2. Time-based aggregations
SELECT 
    YEAR(SaleDate) as Year,
    MONTH(SaleDate) as Month,
    SUM(SalesAmount) as MonthlySales,
    LAG(SUM(SalesAmount)) OVER (ORDER BY YEAR(SaleDate), MONTH(SaleDate)) as PreviousMonth
FROM SalesData
GROUP BY YEAR(SaleDate), MONTH(SaleDate)
ORDER BY Year, Month;

-- 3. Time gaps and missing data detection
SELECT 
    Timestamp,
    LEAD(Timestamp) OVER (ORDER BY Timestamp) as NextTimestamp,
    DATEDIFF(MINUTE, Timestamp, LEAD(Timestamp) OVER (ORDER BY Timestamp)) as GapInMinutes
FROM ServerMetrics
WHERE ServerName = 'SERVER-1'
    AND DATEDIFF(MINUTE, Timestamp, LEAD(Timestamp) OVER (ORDER BY Timestamp)) > 60
ORDER BY Timestamp;

-- 4. Seasonal patterns analysis
SELECT 
    DATEPART(HOUR, Timestamp) as Hour,
    AVG(CPUUsage) as AvgCPU,
    MIN(CPUUsage) as MinCPU,
    MAX(CPUUsage) as MaxCPU
FROM ServerMetrics
GROUP BY DATEPART(HOUR, Timestamp)
ORDER BY Hour;
```
