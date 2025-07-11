# MSSQL Date Format Codes Cheatsheet

## DATEPART Function Date Part Names

| Date Part | Abbreviation | Description | Range |
|-----------|--------------|-------------|-------|
| year | yy, yyyy | Year | 1753-9999 |
| quarter | qq, q | Quarter | 1-4 |
| month | mm, m | Month | 1-12 |
| dayofyear | dy, y | Day of year | 1-366 |
| day | dd, d | Day | 1-31 |
| week | wk, ww | Week | 1-53 |
| weekday | dw, w | Day of week | 1-7 (Sunday=1) |
| hour | hh | Hour | 0-23 |
| minute | mi, n | Minute | 0-59 |
| second | ss, s | Second | 0-59 |
| millisecond | ms | Millisecond | 0-999 |
| microsecond | mcs | Microsecond | 0-999999 |
| nanosecond | ns | Nanosecond | 0-999999999 |
| tzoffset | tz | Timezone offset in minutes | -840 to +840 |
| iso_week | isowk, isoww | ISO week | 1-53 |

### Usage Examples

```sql
-- Get current year
SELECT DATEPART(year, GETDATE())
SELECT DATEPART(yyyy, GETDATE())

-- Get day of week (1=Sunday, 7=Saturday)
SELECT DATEPART(weekday, GETDATE())
SELECT DATEPART(dw, GETDATE())

-- Get hour from datetime
SELECT DATEPART(hour, GETDATE())
SELECT DATEPART(hh, GETDATE())
```


## FORMAT Function Format Codes

### Year Formats
| Format Code | Description | Example Output | Sample Usage |
|-------------|-------------|----------------|--------------|
| y | Year (1-2 digits) | 24 | `FORMAT(GETDATE(), 'y')` |
| yy | Year (2 digits) | 24 | `FORMAT(GETDATE(), 'yy')` |
| yyyy | Year (4 digits) | 2024 | `FORMAT(GETDATE(), 'yyyy')` |

### Month Formats
| Format Code | Description | Example Output | Sample Usage |
|-------------|-------------|----------------|--------------|
| M | Month (1-2 digits) | 1, 12 | `FORMAT(GETDATE(), 'M')` |
| MM | Month (2 digits) | 01, 12 | `FORMAT(GETDATE(), 'MM')` |
| MMM | Month (3-letter abbreviation) | Jan, Dec | `FORMAT(GETDATE(), 'MMM')` |
| MMMM | Month (full name) | January, December | `FORMAT(GETDATE(), 'MMMM')` |

### Day Formats
| Format Code | Description | Example Output | Sample Usage |
|-------------|-------------|----------------|--------------|
| d | Day (1-2 digits) | 5, 25 | `FORMAT(GETDATE(), 'd')` |
| dd | Day (2 digits) | 05, 25 | `FORMAT(GETDATE(), 'dd')` |
| ddd | Day of week (3-letter abbreviation) | Mon, Fri | `FORMAT(GETDATE(), 'ddd')` |
| dddd | Day of week (full name) | Monday, Friday | `FORMAT(GETDATE(), 'dddd')` |

### Hour Formats
| Format Code | Description | Example Output | Sample Usage |
|-------------|-------------|----------------|--------------|
| h | Hour 12-hour (1-2 digits) | 1, 12 | `FORMAT(GETDATE(), 'h')` |
| hh | Hour 12-hour (2 digits) | 01, 12 | `FORMAT(GETDATE(), 'hh')` |
| H | Hour 24-hour (1-2 digits) | 1, 23 | `FORMAT(GETDATE(), 'H')` |
| HH | Hour 24-hour (2 digits) | 01, 23 | `FORMAT(GETDATE(), 'HH')` |

### Minute Formats
| Format Code | Description | Example Output | Sample Usage |
|-------------|-------------|----------------|--------------|
| m | Minute (1-2 digits) | 5, 45 | `FORMAT(GETDATE(), 'm')` |
| mm | Minute (2 digits) | 05, 45 | `FORMAT(GETDATE(), 'mm')` |

### Second Formats
| Format Code | Description | Example Output | Sample Usage |
|-------------|-------------|----------------|--------------|
| s | Second (1-2 digits) | 5, 45 | `FORMAT(GETDATE(), 's')` |
| ss | Second (2 digits) | 05, 45 | `FORMAT(GETDATE(), 'ss')` |
| f | Fraction of second (1 digit) | 1 | `FORMAT(GETDATE(), 'f')` |
| ff | Fraction of second (2 digits) | 12 | `FORMAT(GETDATE(), 'ff')` |
| fff | Fraction of second (3 digits) | 123 | `FORMAT(GETDATE(), 'fff')` |
| ffff | Fraction of second (4 digits) | 1234 | `FORMAT(GETDATE(), 'ffff')` |
| fffff | Fraction of second (5 digits) | 12345 | `FORMAT(GETDATE(), 'fffff')` |
| ffffff | Fraction of second (6 digits) | 123456 | `FORMAT(GETDATE(), 'ffffff')` |
| fffffff | Fraction of second (7 digits) | 1234567 | `FORMAT(GETDATE(), 'fffffff')` |

### AM/PM Formats
| Format Code | Description | Example Output | Sample Usage |
|-------------|-------------|----------------|--------------|
| t | AM/PM (1 character) | A, P | `FORMAT(GETDATE(), 't')` |
| tt | AM/PM (2 characters) | AM, PM | `FORMAT(GETDATE(), 'tt')` |

### Common Format Patterns
| Pattern | Description | Example Output | Sample Usage |
|---------|-------------|----------------|--------------|
| yyyy-MM-dd | ISO date format | 2024-01-15 | `FORMAT(GETDATE(), 'yyyy-MM-dd')` |
| MM/dd/yyyy | US date format | 01/15/2024 | `FORMAT(GETDATE(), 'MM/dd/yyyy')` |
| dd/MM/yyyy | European date format | 15/01/2024 | `FORMAT(GETDATE(), 'dd/MM/yyyy')` |
| yyyy-MM-dd HH:mm:ss | ISO datetime format | 2024-01-15 14:30:25 | `FORMAT(GETDATE(), 'yyyy-MM-dd HH:mm:ss')` |
| MMMM d, yyyy | Long date format | January 15, 2024 | `FORMAT(GETDATE(), 'MMMM d, yyyy')` |
| dddd, MMMM d, yyyy | Full date format | Monday, January 15, 2024 | `FORMAT(GETDATE(), 'dddd, MMMM d, yyyy')` |
| hh:mm:ss tt | 12-hour time format | 02:30:25 PM | `FORMAT(GETDATE(), 'hh:mm:ss tt')` |
| HH:mm:ss | 24-hour time format | 14:30:25 | `FORMAT(GETDATE(), 'HH:mm:ss')` |

## CONVERT Function Style Codes

### Common CONVERT Styles
| Style Code | Format | Example Output | Sample Usage |
|------------|--------|----------------|--------------|
| 0 or 100 | mon dd yyyy hh:miAM/PM | Jan 15 2024 2:30PM | `CONVERT(VARCHAR, GETDATE(), 0)` |
| 1 or 101 | MM/dd/yyyy | 01/15/2024 | `CONVERT(VARCHAR, GETDATE(), 1)` |
| 2 or 102 | yyyy.MM.dd | 2024.01.15 | `CONVERT(VARCHAR, GETDATE(), 2)` |
| 3 or 103 | dd/MM/yyyy | 15/01/2024 | `CONVERT(VARCHAR, GETDATE(), 3)` |
| 4 or 104 | dd.MM.yyyy | 15.01.2024 | `CONVERT(VARCHAR, GETDATE(), 4)` |
| 5 or 105 | dd-MM-yyyy | 15-01-2024 | `CONVERT(VARCHAR, GETDATE(), 5)` |
| 6 or 106 | dd mon yyyy | 15 Jan 2024 | `CONVERT(VARCHAR, GETDATE(), 6)` |
| 7 or 107 | mon dd, yyyy | Jan 15, 2024 | `CONVERT(VARCHAR, GETDATE(), 7)` |
| 8 or 108 | HH:mm:ss | 14:30:25 | `CONVERT(VARCHAR, GETDATE(), 8)` |
| 9 or 109 | mon dd yyyy hh:mi:ss:mmmAM/PM | Jan 15 2024 2:30:25:123PM | `CONVERT(VARCHAR, GETDATE(), 9)` |
| 10 or 110 | MM-dd-yyyy | 01-15-2024 | `CONVERT(VARCHAR, GETDATE(), 10)` |
| 11 or 111 | yyyy/MM/dd | 2024/01/15 | `CONVERT(VARCHAR, GETDATE(), 11)` |
| 12 or 112 | yyyyMMdd | 20240115 | `CONVERT(VARCHAR, GETDATE(), 12)` |
| 13 or 113 | dd mon yyyy HH:mm:ss:mmm | 15 Jan 2024 14:30:25:123 | `CONVERT(VARCHAR, GETDATE(), 13)` |
| 14 or 114 | HH:mm:ss:mmm | 14:30:25:123 | `CONVERT(VARCHAR, GETDATE(), 14)` |
| 20 or 120 | yyyy-MM-dd HH:mm:ss | 2024-01-15 14:30:25 | `CONVERT(VARCHAR, GETDATE(), 20)` |
| 21 or 121 | yyyy-MM-dd HH:mm:ss.mmm | 2024-01-15 14:30:25.123 | `CONVERT(VARCHAR, GETDATE(), 21)` |
| 23 or 123 | yyyy-MM-dd | 2024-01-15 | `CONVERT(VARCHAR, GETDATE(), 23)` |
| 24 or 124 | HH:mm:ss | 14:30:25 | `CONVERT(VARCHAR, GETDATE(), 24)` |
| 25 or 125 | yyyy-MM-dd HH:mm:ss.mmm | 2024-01-15 14:30:25.123 | `CONVERT(VARCHAR, GETDATE(), 25)` |
| 126 | yyyy-MM-ddTHH:mm:ss.mmm | 2024-01-15T14:30:25.123 | `CONVERT(VARCHAR, GETDATE(), 126)` |
| 127 | yyyy-MM-ddTHH:mm:ss.mmmZ | 2024-01-15T14:30:25.123Z | `CONVERT(VARCHAR, GETDATE(), 127)` |
| 130 | dd mon yyyy hh:mi:ss:mmmAM | 15 Jan 2024 2:30:25:123PM | `CONVERT(VARCHAR, GETDATE(), 130)` |
| 131 | dd/MM/yyyy hh:mi:ss:mmmAM | 15/01/2024 2:30:25:123PM | `CONVERT(VARCHAR, GETDATE(), 131)` |

## Usage Examples

### FORMAT Function Examples
```sql
-- Custom formats
SELECT FORMAT(GETDATE(), 'yyyy-MM-dd')                    -- 2024-01-15
SELECT FORMAT(GETDATE(), 'dddd, MMMM d, yyyy')           -- Monday, January 15, 2024
SELECT FORMAT(GETDATE(), 'hh:mm:ss tt')                  -- 02:30:25 PM
SELECT FORMAT(GETDATE(), 'yyyy-MM-dd HH:mm:ss.fff')      -- 2024-01-15 14:30:25.123

-- With culture
SELECT FORMAT(GETDATE(), 'D', 'en-US')                   -- Monday, January 15, 2024
SELECT FORMAT(GETDATE(), 'D', 'fr-FR')                   -- lundi 15 janvier 2024
```

### CONVERT Function Examples
```sql
-- Standard formats
SELECT CONVERT(VARCHAR, GETDATE(), 101)                   -- 01/15/2024
SELECT CONVERT(VARCHAR, GETDATE(), 103)                   -- 15/01/2024
SELECT CONVERT(VARCHAR, GETDATE(), 120)                   -- 2024-01-15 14:30:25
SELECT CONVERT(VARCHAR, GETDATE(), 126)                   -- 2024-01-15T14:30:25.123
```

## Notes

- **FORMAT Function**: More flexible, supports culture-specific formatting, available in SQL Server 2012+
- **CONVERT Function**: Traditional method, faster performance, limited formatting options
- **Case Sensitivity**: Format codes are case-sensitive (M = month, m = minute)
- **Performance**: CONVERT is generally faster than FORMAT for simple conversions
- **Culture Support**: FORMAT function supports culture-specific formatting with optional culture parameter
