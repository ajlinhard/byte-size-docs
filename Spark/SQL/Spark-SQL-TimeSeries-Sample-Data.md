# Spark SQL TimeSeries Sample Data
Spark SQL has different syntax for data generation and function:

**Key Spark SQL Differences:**

1. **Data Generation**: Uses `sequence()` and `explode()` functions instead of recursive CTEs
2. **Random Functions**: Uses `hash()` and `rand()` instead of `CHECKSUM(NEWID())`
3. **Date/Time Functions**: Uses `to_date()`, `to_timestamp()`, `dayofyear()`, etc.
4. **Temporary Views**: Creates temporary views instead of physical tables by default
5. **Mathematical Functions**: Uses `sin()`, `cos()`, `pi()` directly

**Enhanced Features:**

- **Delta Lake Support**: Commented code to create persistent Delta tables
- **Advanced Analytics**: Added more sophisticated queries including:
  - Time series resampling (15-minute windows from 5-minute data)
  - Stock volatility calculations with first/last value functions
  - Anomaly detection using z-scores
  - Rolling statistics with configurable windows
  - Percentile calculations

**Spark-Specific Optimizations:**

- Uses `PARTITION BY` effectively for window functions
- Leverages `date_trunc()` for time bucketing
- Includes `unix_timestamp()` for precise time calculations
- Uses `percentile_approx()` for efficient percentile calculations

The data maintains the same realistic patterns (seasonal variations, random noise) while being optimized for Spark's distributed computing model. You can run this directly in Databricks, Spark SQL, or any Spark environment.

---
# Code
```sql
-- Spark SQL Timeseries Test Data
-- This script creates sample tables with various timeseries patterns for testing

-- 1. Sales Data - Daily sales with seasonal patterns
CREATE OR REPLACE TEMPORARY VIEW SalesData AS
WITH DateSeries AS (
  SELECT explode(sequence(
    to_date('2023-01-01'), 
    to_date('2024-12-31'), 
    interval 1 day
  )) AS SaleDate
),
SalesWithRandom AS (
  SELECT 
    SaleDate,
    (abs(hash(SaleDate, rand())) % 5) + 1 AS ProductID,
    round(1000 + (500 * sin(dayofyear(SaleDate) * 2 * pi() / 365)) + (abs(hash(SaleDate, rand())) % 500), 2) AS SalesAmount,
    10 + (abs(hash(SaleDate, rand())) % 20) AS Quantity,
    CASE (abs(hash(SaleDate, rand())) % 4)
      WHEN 0 THEN 'North'
      WHEN 1 THEN 'South'
      WHEN 2 THEN 'East'
      ELSE 'West'
    END AS Region
  FROM DateSeries
)
SELECT * FROM SalesWithRandom;

-- 2. Server Metrics - Hourly CPU and Memory usage
CREATE OR REPLACE TEMPORARY VIEW ServerMetrics AS
WITH HourSeries AS (
  SELECT explode(sequence(
    to_timestamp('2025-06-08 00:00:00'), 
    to_timestamp('2025-07-08 00:00:00'), 
    interval 1 hour
  )) AS Timestamp
),
MetricsWithRandom AS (
  SELECT 
    Timestamp,
    concat('SERVER-', cast((abs(hash(Timestamp, rand())) % 3) + 1 as string)) AS ServerName,
    round(20 + (30 * sin(hour(Timestamp) * pi() / 12)) + (abs(hash(Timestamp, rand())) % 20), 2) AS CPUUsage,
    round(40 + (20 * cos(hour(Timestamp) * pi() / 12)) + (abs(hash(Timestamp, rand())) % 15), 2) AS MemoryUsage,
    100 + (abs(hash(Timestamp, rand())) % 200) AS DiskIO
  FROM HourSeries
)
SELECT * FROM MetricsWithRandom;

-- 3. Stock Prices - Minute-by-minute stock data
CREATE OR REPLACE TEMPORARY VIEW StockPrices AS
WITH TradingDays AS (
  SELECT explode(sequence(
    to_date('2025-07-01'), 
    to_date('2025-07-07'), 
    interval 1 day
  )) AS TradeDate
),
TradingHours AS (
  SELECT explode(sequence(9, 16, 1)) AS TradeHour
),
TradingMinutes AS (
  SELECT explode(sequence(0, 59, 1)) AS TradeMinute
),
TradingTimestamps AS (
  SELECT 
    to_timestamp(concat(
      cast(d.TradeDate as string), ' ',
      lpad(cast(h.TradeHour as string), 2, '0'), ':',
      lpad(cast(m.TradeMinute as string), 2, '0'), ':00'
    )) AS Timestamp
  FROM TradingDays d
  CROSS JOIN TradingHours h
  CROSS JOIN TradingMinutes m
  WHERE dayofweek(d.TradeDate) NOT IN (1, 7) -- Exclude weekends
    AND NOT (h.TradeHour = 16 AND m.TradeMinute > 0) -- Stop at 4:00 PM
),
StockData AS (
  SELECT 
    Timestamp,
    CASE (abs(hash(Timestamp, rand())) % 3)
      WHEN 0 THEN 'AAPL'
      WHEN 1 THEN 'GOOGL'
      ELSE 'MSFT'
    END AS Symbol,
    round(100 + (abs(hash(Timestamp, rand())) % 50) + (0.01 * abs(hash(Timestamp, rand())) % 100)), 4) AS OpenPrice,
    round(100 + (abs(hash(Timestamp, rand())) % 50) + (0.01 * abs(hash(Timestamp, rand())) % 100)), 4) AS ClosePrice,
    round(100 + (abs(hash(Timestamp, rand())) % 50) + (0.01 * abs(hash(Timestamp, rand())) % 100)), 4) AS HighPrice,
    round(100 + (abs(hash(Timestamp, rand())) % 50) + (0.01 * abs(hash(Timestamp, rand())) % 100)), 4) AS LowPrice,
    (abs(hash(Timestamp, rand())) % 100000) + 1000 AS Volume
  FROM TradingTimestamps
)
SELECT * FROM StockData;

-- 4. IoT Sensor Data - Temperature readings every 5 minutes
CREATE OR REPLACE TEMPORARY VIEW IoTSensorData AS
WITH SensorReadings AS (
  SELECT explode(sequence(
    to_timestamp('2025-07-01 00:00:00'), 
    to_timestamp('2025-07-08 00:00:00'), 
    interval 5 minutes
  )) AS Timestamp
),
SensorData AS (
  SELECT 
    Timestamp,
    concat('SENSOR-', lpad(cast((abs(hash(Timestamp, rand())) % 10) + 1 as string), 3, '0')) AS SensorID,
    round(20 + (10 * sin(hour(Timestamp) * pi() / 12)) + (abs(hash(Timestamp, rand())) % 10), 2) AS Temperature,
    round(45 + (abs(hash(Timestamp, rand())) % 30), 2) AS Humidity,
    round(1013.25 + (abs(hash(Timestamp, rand())) % 20) - 10, 2) AS Pressure,
    CASE (abs(hash(Timestamp, rand())) % 5)
      WHEN 0 THEN 'Warehouse A'
      WHEN 1 THEN 'Warehouse B'
      WHEN 2 THEN 'Office Building'
      WHEN 3 THEN 'Data Center'
      ELSE 'Manufacturing Floor'
    END AS Location
  FROM SensorReadings
)
SELECT * FROM SensorData;

-- 5. Website Analytics - Page views by hour
CREATE OR REPLACE TEMPORARY VIEW WebAnalytics AS
WITH WebHours AS (
  SELECT explode(sequence(
    to_timestamp('2025-06-24 00:00:00'), 
    to_timestamp('2025-07-08 00:00:00'), 
    interval 1 hour
  )) AS Timestamp
),
WebData AS (
  SELECT 
    Timestamp,
    CASE (abs(hash(Timestamp, rand())) % 6)
      WHEN 0 THEN '/home'
      WHEN 1 THEN '/products'
      WHEN 2 THEN '/about'
      WHEN 3 THEN '/contact'
      WHEN 4 THEN '/blog'
      ELSE '/support'
    END AS PageURL,
    10 + (abs(hash(Timestamp, rand())) % 190) AS PageViews,
    5 + (abs(hash(Timestamp, rand())) % 95) AS UniqueVisitors,
    round(20 + (abs(hash(Timestamp, rand())) % 60), 2) AS BounceRate,
    60 + (abs(hash(Timestamp, rand())) % 300) AS AvgSessionDuration
  FROM WebHours
)
SELECT * FROM WebData;

-- Optionally create persistent tables (uncomment if needed)
/*
CREATE TABLE sales_data USING DELTA AS SELECT * FROM SalesData;
CREATE TABLE server_metrics USING DELTA AS SELECT * FROM ServerMetrics;
CREATE TABLE stock_prices USING DELTA AS SELECT * FROM StockPrices;
CREATE TABLE iot_sensor_data USING DELTA AS SELECT * FROM IoTSensorData;
CREATE TABLE web_analytics USING DELTA AS SELECT * FROM WebAnalytics;
*/

-- Sample queries to test timeseries functionality

-- 1. Moving average of sales using window functions
SELECT 
  SaleDate,
  SalesAmount,
  avg(SalesAmount) OVER (
    ORDER BY SaleDate 
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS MovingAvg7Days
FROM SalesData
WHERE ProductID = 1
ORDER BY SaleDate;

-- 2. Time-based aggregations with lag function
SELECT 
  year(SaleDate) as Year,
  month(SaleDate) as Month,
  sum(SalesAmount) as MonthlySales,
  lag(sum(SalesAmount)) OVER (ORDER BY year(SaleDate), month(SaleDate)) as PreviousMonth,
  round(
    (sum(SalesAmount) - lag(sum(SalesAmount)) OVER (ORDER BY year(SaleDate), month(SaleDate))) 
    / lag(sum(SalesAmount)) OVER (ORDER BY year(SaleDate), month(SaleDate)) * 100, 2
  ) as MonthOverMonthPct
FROM SalesData
GROUP BY year(SaleDate), month(SaleDate)
ORDER BY Year, Month;

-- 3. Time gaps and missing data detection
WITH ServerGaps AS (
  SELECT 
    Timestamp,
    lead(Timestamp) OVER (PARTITION BY ServerName ORDER BY Timestamp) as NextTimestamp,
    ServerName
  FROM ServerMetrics
)
SELECT 
  Timestamp,
  NextTimestamp,
  ServerName,
  (unix_timestamp(NextTimestamp) - unix_timestamp(Timestamp)) / 60 as GapInMinutes
FROM ServerGaps
WHERE (unix_timestamp(NextTimestamp) - unix_timestamp(Timestamp)) / 60 > 60
  AND ServerName = 'SERVER-1'
ORDER BY Timestamp;

-- 4. Seasonal patterns analysis with percentiles
SELECT 
  hour(Timestamp) as Hour,
  avg(CPUUsage) as AvgCPU,
  min(CPUUsage) as MinCPU,
  max(CPUUsage) as MaxCPU,
  percentile_approx(CPUUsage, 0.5) as MedianCPU,
  percentile_approx(CPUUsage, 0.95) as P95CPU
FROM ServerMetrics
GROUP BY hour(Timestamp)
ORDER BY Hour;

-- 5. Daily aggregations with rolling statistics
SELECT 
  date(Timestamp) as Date,
  sum(PageViews) as DailyPageViews,
  avg(sum(PageViews)) OVER (
    ORDER BY date(Timestamp) 
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) as WeeklyAvgPageViews,
  stddev(sum(PageViews)) OVER (
    ORDER BY date(Timestamp) 
    ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
  ) as MonthlyStdDev
FROM WebAnalytics
GROUP BY date(Timestamp)
ORDER BY Date;

-- 6. Time series resampling - 15-minute aggregations from 5-minute data
SELECT 
  date_trunc('minute', 
    from_unixtime(
      floor(unix_timestamp(Timestamp) / 900) * 900
    )
  ) as FifteenMinuteWindow,
  SensorID,
  avg(Temperature) as AvgTemperature,
  min(Temperature) as MinTemperature,
  max(Temperature) as MaxTemperature,
  count(*) as ReadingCount
FROM IoTSensorData
WHERE SensorID = 'SENSOR-001'
GROUP BY 
  date_trunc('minute', 
    from_unixtime(
      floor(unix_timestamp(Timestamp) / 900) * 900
    )
  ),
  SensorID
ORDER BY FifteenMinuteWindow;

-- 7. Stock price volatility calculation
SELECT 
  Symbol,
  date(Timestamp) as TradeDate,
  min(LowPrice) as DayLow,
  max(HighPrice) as DayHigh,
  first_value(OpenPrice) OVER (
    PARTITION BY Symbol, date(Timestamp) 
    ORDER BY Timestamp
  ) as DayOpen,
  last_value(ClosePrice) OVER (
    PARTITION BY Symbol, date(Timestamp) 
    ORDER BY Timestamp
    RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
  ) as DayClose,
  round(
    (max(HighPrice) - min(LowPrice)) / first_value(OpenPrice) OVER (
      PARTITION BY Symbol, date(Timestamp) 
      ORDER BY Timestamp
    ) * 100, 2
  ) as DayVolatilityPct
FROM StockPrices
GROUP BY Symbol, date(Timestamp), Timestamp, OpenPrice, ClosePrice
ORDER BY Symbol, TradeDate;

-- 8. Anomaly detection using z-score
WITH StatsBase AS (
  SELECT 
    ServerName,
    avg(CPUUsage) as AvgCPU,
    stddev(CPUUsage) as StdCPU
  FROM ServerMetrics
  GROUP BY ServerName
)
SELECT 
  s.Timestamp,
  s.ServerName,
  s.CPUUsage,
  sb.AvgCPU,
  sb.StdCPU,
  round((s.CPUUsage - sb.AvgCPU) / sb.StdCPU, 2) as ZScore,
  CASE 
    WHEN abs((s.CPUUsage - sb.AvgCPU) / sb.StdCPU) > 2 THEN 'Anomaly'
    ELSE 'Normal'
  END as AnomalyFlag
FROM ServerMetrics s
JOIN StatsBase sb ON s.ServerName = sb.ServerName
WHERE abs((s.CPUUsage - sb.AvgCPU) / sb.StdCPU) > 2
ORDER BY s.ServerName, s.Timestamp;
```
