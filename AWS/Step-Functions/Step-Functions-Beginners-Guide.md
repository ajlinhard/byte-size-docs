# AWS Step Functions — A Beginner's Guide

Step Functions is AWS's workflow orchestration service. You define a **state machine** — a flowchart of steps your application runs through — and AWS handles executing them, retrying failures, and tracking state. Think of it as a conductor for your microservices.

---

## The Core Concept: States

Everything in Step Functions is a **state**. Your state machine is a JSON document (called Amazon States Language, or ASL) that describes a graph of states and how to move between them. Here are all the state types:

---

### 1. Task State
This is the workhorse. It does actual work — usually invokes a Lambda, calls an ECS task, hits an API, etc.

```python
# Terraform example of a basic state machine with one Task
resource "aws_sfn_state_machine" "my_machine" {
  name     = "my-first-state-machine"
  role_arn = aws_iam_role.sfn_role.arn

  definition = jsonencode({
    Comment = "A simple example"
    StartAt = "ProcessOrder"
    States = {
      ProcessOrder = {
        Type     = "Task"
        Resource = "arn:aws:lambda:us-east-1:123456789:function:process-order"
        End      = true
      }
    }
  })
}
```

The `Resource` field points to what runs. Common resources are:
- `arn:aws:states:::lambda:invoke` — Lambda functions
- `arn:aws:states:::ecs:runTask` — ECS/Fargate containers
- `arn:aws:states:::dynamodb:putItem` — DynamoDB directly (no Lambda needed)
- `arn:aws:states:::sqs:sendMessage` — SQS queues
- `arn:aws:states:::sns:publish` — SNS topics

---

### 2. Choice State
A conditional branch — like an `if/else` or `switch`. It evaluates the current input and routes to different states.

```python
definition = jsonencode({
  StartAt = "CheckOrderValue"
  States = {
    CheckOrderValue = {
      Type = "Choice"
      Choices = [
        {
          Variable    = "$.orderTotal"
          NumericGreaterThan = 1000
          Next        = "RequireApproval"
        },
        {
          Variable    = "$.orderTotal"
          NumericLessThanEquals = 1000
          Next        = "AutoApprove"
        }
      ]
      Default = "AutoApprove"  # fallback if no condition matches
    }
    RequireApproval = { Type = "Task", Resource = "...", End = true }
    AutoApprove     = { Type = "Task", Resource = "...", End = true }
  }
})
```

Choice states **cannot** have an `End` field — they always route to another state.

---

### 3. Wait State
Pauses execution for a fixed duration or until a specific timestamp. Great for scheduled retries or time-based workflows.

```python
WaitForCooldown = {
  Type    = "Wait"
  Seconds = 300        # wait 5 minutes
  Next    = "RetryPayment"
}

# OR wait until a specific time from your input
WaitUntilScheduled = {
  Type           = "Wait"
  TimestampPath  = "$.scheduledTime"  # e.g. "2026-05-01T09:00:00Z"
  Next           = "SendReminder"
}
```

---

### 4. Parallel State — Running Things Side by Side
This is how you run independent work **concurrently**. Each branch runs simultaneously, and the Parallel state only moves on when **all branches complete**.

```python
ProcessOrderInParallel = {
  Type = "Parallel"
  Branches = [
    {
      StartAt = "ChargePayment"
      States = {
        ChargePayment = {
          Type     = "Task"
          Resource = "arn:aws:lambda:...:function:charge-payment"
          End      = true
        }
      }
    },
    {
      StartAt = "ReserveInventory"
      States = {
        ReserveInventory = {
          Type     = "Task"
          Resource = "arn:aws:lambda:...:function:reserve-inventory"
          End      = true
        }
      }
    },
    {
      StartAt = "SendConfirmationEmail"
      States = {
        SendConfirmationEmail = {
          Type     = "Task"
          Resource = "arn:aws:lambda:...:function:send-email"
          End      = true
        }
      }
    }
  ]
  Next = "FulfillOrder"
}
```

The **output** of a Parallel state is an **array** — one element per branch — so your next state receives `[paymentResult, inventoryResult, emailResult]`.

---

### 5. Map State — Parallel over a List
Like a `forEach` that runs in parallel. If you have an array in your input (say, 50 order line items), Map will fan out and process each one concurrently.

```python
ProcessLineItems = {
  Type           = "Map"
  ItemsPath      = "$.lineItems"     # the array in your input
  MaxConcurrency = 10                # process up to 10 at a time (0 = unlimited)
  Iterator = {
    StartAt = "ProcessItem"
    States = {
      ProcessItem = {
        Type     = "Task"
        Resource = "arn:aws:lambda:...:function:process-line-item"
        End      = true
      }
    }
  }
  Next = "AggregateResults"
}
```

`MaxConcurrency` is important — set it to avoid overwhelming downstream services.

---

### 6. Pass State
Passes input to output without doing any work. Useful for injecting static data or reshaping your state during development/testing.

```python
InjectDefaults = {
  Type   = "Pass"
  Result = { currency = "USD", taxRate = 0.08 }
  Next   = "ProcessOrder"
}
```

---

### 7. Succeed and Fail States
Terminal states that explicitly end the execution.

```python
OrderComplete = {
  Type = "Succeed"
}

PaymentFailed = {
  Type  = "Fail"
  Error = "PaymentError"
  Cause = "Credit card was declined"
}
```

---

## Running Things in Series

Series is the default — just chain states with `Next`:

```python
definition = jsonencode({
  StartAt = "ValidateOrder"
  States = {
    ValidateOrder = {
      Type     = "Task"
      Resource = "arn:aws:lambda:...:function:validate"
      Next     = "ChargePayment"       # 👈 goes here next
    }
    ChargePayment = {
      Type     = "Task"
      Resource = "arn:aws:lambda:...:function:charge"
      Next     = "ShipOrder"
    }
    ShipOrder = {
      Type     = "Task"
      Resource = "arn:aws:lambda:...:function:ship"
      End      = true                  # 👈 done
    }
  }
})
```

---

## Wiring It All Together — A Real Example

Here's an order processing workflow combining series, parallel, choice, and wait:

```
ValidateOrder → [Parallel: ChargePayment + ReserveInventory] 
              → CheckStock (Choice)
                  → InStock? → ShipOrder → Done
                  → OutOfStock? → WaitForRestock (Wait 24h) → ShipOrder → Done
```

```python
definition = jsonencode({
  StartAt = "ValidateOrder"
  States = {
    ValidateOrder = {
      Type     = "Task"
      Resource = "arn:aws:lambda:...:function:validate"
      Next     = "PaymentAndInventory"
    }

    PaymentAndInventory = {
      Type = "Parallel"
      Branches = [
        {
          StartAt = "ChargePayment"
          States  = { ChargePayment = { Type = "Task", Resource = "...", End = true } }
        },
        {
          StartAt = "ReserveInventory"
          States  = { ReserveInventory = { Type = "Task", Resource = "...", End = true } }
        }
      ]
      Next = "CheckStock"
    }

    CheckStock = {
      Type = "Choice"
      Choices = [
        { Variable = "$.inStock", BooleanEquals = true, Next = "ShipOrder" }
      ]
      Default = "WaitForRestock"
    }

    WaitForRestock = {
      Type    = "Wait"
      Seconds = 86400   # 24 hours
      Next    = "ShipOrder"
    }

    ShipOrder = {
      Type     = "Task"
      Resource = "arn:aws:lambda:...:function:ship"
      End      = true
    }
  }
})
```

---

## Waiting on External Dependencies — Callbacks

Sometimes a Task needs to wait for something *outside* AWS — a human approval, a third-party webhook, a payment processor. Use the **`.waitForTaskToken`** pattern:

```python
WaitForHumanApproval = {
  Type     = "Task"
  Resource = "arn:aws:states:::lambda:invoke.waitForTaskToken"  # 👈 key part
  Parameters = {
    FunctionName = "send-approval-email"
    Payload = {
      "taskToken.$" = "$$.Task.Token"   # injects the callback token
      "orderId.$"   = "$.orderId"
    }
  }
  HeartbeatSeconds = 3600   # fail if no callback within 1 hour
  Next = "ProcessApproval"
}
```

Your Lambda emails an approver with a link. When they click approve/reject, your system calls `sfn.send_task_success(taskToken, output)` or `sfn.send_task_failure(...)`, and the workflow resumes. The execution can wait **up to a year** like this with zero cost while idle.

---

## Error Handling and Retries

Every Task state can have `Retry` and `Catch` blocks:

```python
ChargePayment = {
  Type     = "Task"
  Resource = "arn:aws:lambda:...:function:charge"
  
  Retry = [
    {
      ErrorEquals     = ["Lambda.ServiceException", "Lambda.TooManyRequestsException"]
      IntervalSeconds = 2       # first retry after 2s
      MaxAttempts     = 3       # try up to 3 times
      BackoffRate     = 2.0     # double the wait each retry (2s, 4s, 8s)
    }
  ]

  Catch = [
    {
      ErrorEquals = ["PaymentDeclinedError"]
      Next        = "NotifyCustomer"     # route to a specific state on failure
      ResultPath  = "$.error"            # attach error info to your state
    },
    {
      ErrorEquals = ["States.ALL"]       # catch anything else
      Next        = "GenericErrorHandler"
    }
  ]

  Next = "ShipOrder"
}
```

---

## Key Concepts to Keep in Mind

**Input/Output and `$`** — Every state receives JSON input and produces JSON output. The `$` symbol refers to the current state's data, and `$.fieldName` drills into it. `$$` refers to execution context (like the task token above).

**Express vs Standard workflows** — Standard can run for up to a year, charges per state transition, and guarantees exactly-once execution. Express runs for up to 5 minutes, charges per duration, and is better for high-volume event processing.

**IAM Role** — Your state machine needs an IAM role with permissions to invoke every resource it touches (Lambda ARNs, DynamoDB tables, etc.). This is the most common gotcha when starting out.

The mental model to keep: Step Functions is the **glue** between your services. Your Lambdas stay small and single-purpose, and Step Functions handles all the "what happens next, what if it fails, run these in parallel" logic that would otherwise be tangled inside application code.
