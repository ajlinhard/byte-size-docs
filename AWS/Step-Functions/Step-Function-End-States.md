## Ending an AWS Step Functions Execution

There are several ways to end a Step Functions state machine execution:

---

### 1. **Natural Completion**
The execution ends automatically when it reaches a **terminal state** — a state with no `Next` field or marked as an end state:
```json
"MyLastState": {
  "Type": "Task",
  "Resource": "arn:aws:lambda:...",
  "End": true
}
```

---

### 2. **Succeed State**
Stops execution successfully and optionally passes output:
```json
"Done": {
  "Type": "Succeed"
}
```

---

### 3. **Fail State**
Stops execution and marks it as a **failure** with an error and cause:
```json
"JobFailed": {
  "Type": "Fail",
  "Error": "JobFailed",
  "Cause": "The job exceeded the time limit."
}
```

---

### 4. **Stop Execution via AWS Console**
1. Go to **AWS Console → Step Functions**
2. Select your state machine
3. Find the running execution
4. Click **"Stop execution"**

---

### 5. **Stop Execution via AWS CLI**
```bash
aws stepfunctions stop-execution \
  --execution-arn arn:aws:states:us-east-1:123456789:execution:MyStateMachine:my-execution-id \
  --error "ManualStop" \
  --cause "Stopped by operator"
```

---

### 6. **Stop Execution via SDK (e.g., Python/Boto3)**
```python
import boto3

client = boto3.client('stepfunctions')

client.stop_execution(
    executionArn='arn:aws:states:us-east-1:123456789:execution:MyStateMachine:my-execution-id',
    error='ManualStop',
    cause='Stopped programmatically'
)
```

---

### Summary Table

| Method | Outcome |
|---|---|
| `"End": true` on a state | ✅ Success |
| `Succeed` state | ✅ Success |
| `Fail` state | ❌ Failure |
| Console / CLI / SDK stop | ❌ Aborted |

The **`Fail` state** and **manual stop** both mark the execution as failed/aborted, while `Succeed` or natural end marks it as successful.
