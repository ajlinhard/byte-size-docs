# Cloud Watch Basics
Cloud Watch is an area of the cloud environment where logging can be captured and query.

## Searching for Term or Value
This query is searching for an ID within a system logs. Likely should add other filters based on timestamp or log stream.
```sql
fields @timestamp, @message
| filter @message like /123722355/
| sort @timestamp desc
| limit 100
```

## Cloud Watch Logs Interface
<img width="2207" height="1109" alt="image" src="https://github.com/user-attachments/assets/80224afe-53ae-4446-bb76-c1f0d0c975f1" />
