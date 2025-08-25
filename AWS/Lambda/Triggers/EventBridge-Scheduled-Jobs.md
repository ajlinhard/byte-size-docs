# EventBridge Scheduled Jobs
You can use the AWS EventBridge to standup the a Lambda Jobs to run on some schedule or off an event pattern (Auto Scaling, EC2, Step Functions, RDS, S3). There are tons of use cases for easy automation of Lambda jobs  to run based of these types of triggers. Whether it is a simple daily task or a complex execution based on some monitoring of your cloud infrastructure like a warning email with a report.

### Documentation:
- [AWS Other Lambda Trigger Integrations](https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html)

## AWS EventBridge (Regularly Scheduled Job)
- [AWS EventBridge based Lambda](https://docs.aws.amazon.com/lambda/latest/dg/with-eventbridge-scheduler.html)
- [Create a Rule Schedule](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-rule-schedule.html)
- [AWS Cron and Rates](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-scheduled-rule-pattern.html#eb-rate-expressions)

The most common and flexible approach is using **Amazon EventBridge** (formerly CloudWatch Events) with cron expressions:

```python
# Example Lambda function
import json

def lambda_handler(event, context):
    # Your scheduled task logic here
    print("Lambda function executed on schedule!")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Task completed successfully')
    }
```

To set up the schedule:

1. **Via AWS Console:**
   - Go to EventBridge → Rules
   - Create a new rule with a schedule
   - Use cron expressions like: `cron(0 9 * * MON-FRI *)` (9 AM weekdays)
   - Set your Lambda function as the target

2. **Via AWS CLI:**
```bash
aws events put-rule \
    --name MyScheduledRule \
    --schedule-expression "rate(1 hour)" \
    --state ENABLED

aws events put-targets \
    --rule MyScheduledRule \
    --targets "Id"="1","Arn"="arn:aws:lambda:region:account:function:MyFunction"
```

3. **Via Terraform:**
```hcl
resource "aws_cloudwatch_event_rule" "lambda_schedule" {
  name                = "lambda-schedule"
  schedule_expression = "cron(0 */6 * * ? *)"  # Every 6 hours
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.lambda_schedule.name
  target_id = "TriggerLambda"
  arn       = aws_lambda_function.my_function.arn
}
```

## Schedule Expression Formats

You can use either:
- **Rate expressions:** `rate(1 hour)`, `rate(30 minutes)`, `rate(1 day)`
- **Cron expressions:** `cron(0 9 * * ? *)` (9 AM daily)

## Key Benefits

- No server management required
- Pay only for execution time
- Automatic scaling and error handling
- Integration with other AWS services
- Built-in monitoring via CloudWatch

Would you like me to help you set up a specific schedule or walk through any particular use case?
