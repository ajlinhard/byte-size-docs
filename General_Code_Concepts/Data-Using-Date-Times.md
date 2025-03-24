# UTC and Common Datetime Formats

## UTC (Coordinated Universal Time)

UTC is a time standard that serves as the basis for civil time worldwide. Key characteristics:

- **Global reference point**: Not a format itself but a time standard
- **No daylight saving**: Doesn't change with seasons
- **Zero offset**: Represented as UTC or UTC+00:00
- **Format example**: `2025-03-24T14:30:00Z` (the 'Z' indicates UTC)
- **Usage**: Ideal for systems operating across time zones, cloud services, and international applications

## Unix Timestamp

A Unix timestamp represents time as the number of seconds elapsed since January 1, 1970, at 00:00:00 UTC (the "Unix Epoch").

- **Format**: A single integer or floating-point number
- **Example**: `1711373400` (represents March 24, 2025, 14:30:00 UTC)
- **Benefits**: Compact, easy to compare and sort, timezone-independent
- **Limitations**: Not human-readable, can't represent dates before 1970, will face the Year 2038 problem on 32-bit systems

## Other Common Datetime Formats

### ISO 8601
The international standard for date and time representation:
- **Format**: `YYYY-MM-DDTHH:MM:SS±hh:mm`
- **Example**: `2025-03-24T14:30:00+00:00` or `2025-03-24T14:30:00Z` (UTC)
- **Benefits**: Unambiguous, internationally recognized, sortable

### RFC 3339
A profile of ISO 8601 used for Internet protocols:
- **Format**: Very similar to ISO 8601
- **Example**: `2025-03-24T14:30:00Z`
- **Usage**: APIs, email headers, network protocols

### RFC 2822
Used primarily in email and web contexts:
- **Format**: `Day, DD Mon YYYY HH:MM:SS ±HHMM`
- **Example**: `Mon, 24 Mar 2025 14:30:00 +0000`
- **Usage**: Email headers, older web applications

### Human-readable formats
Various region-specific formats:
- **US (MM/DD/YYYY)**: `03/24/2025 2:30 PM`
- **Europe (DD/MM/YYYY)**: `24/03/2025 14:30`
- **China/Japan/Korea (YYYY/MM/DD)**: `2025/03/24 14:30`

### Database-specific formats
- **SQL standard**: `TIMESTAMP '2025-03-24 14:30:00'`
- **Oracle**: `24-MAR-25`
- **Microsoft SQL Server**: `2025-03-24T14:30:00.000`

## Best Practices

1. **Storage**: Store dates in UTC or as Unix timestamps
2. **Display**: Convert to local time only at display time
3. **APIs**: Use ISO 8601/RFC 3339 in API communications
4. **Parsing**: Be lenient when accepting dates, strict when generating them
5. **Localization**: Format based on user locale for display purposes

When designing systems, choosing the right datetime format depends on your specific needs for human readability, sorting, storage efficiency, and international compatibility.
