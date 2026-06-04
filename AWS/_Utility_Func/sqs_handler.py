import os
import json
import boto3
from itertools import batched  # requires Python 3.12+


class SQSHandler:
    """
    Simple SQS handler for sending messages and parsing events,
    with support for environment-based queue naming.
    """

    def __init__(self, queue_name=None):
        """
        Initialize SQS handler

        Args:
            queue_name (str): Optional specific queue name. If not provided, uses ENVIRONMENT.
        """
        self.region = "us-gov-east-1"
        self.sqs = boto3.client("sqs", region_name=self.region)

        # Auto-detect AWS account ID
        sts = boto3.client("sts", region_name=self.region)
        account_id = sts.get_caller_identity()["Account"]

        # Determine environment
        env = os.environ.get("ENVIRONMENT", "test").lower()

        # Construct queue name if not provided
        if not queue_name:
            queue_name = f"{env}-claims-check-queue"

        # Construct full queue URL
        self.queue_url = f"https://sqs.{self.region}.amazonaws.com/{account_id}/{queue_name}"

    def send_message(self, message_body):
        """
        Send a message to the SQS queue

        Args:
            message_body (dict): Message to send

        Returns:
            dict: Response with statusCode and SQS message details
        """
        try:
            response = self.sqs.send_message(
                QueueUrl=self.queue_url, MessageBody=json.dumps(message_body)
            )

            return {
                "statusCode": 200,
                "body": {
                    "message": "Message sent to SQS queue",
                    "sqs_message_id": response["MessageId"],
                },
            }

        except Exception as e:
            return {
                "statusCode": 500,
                "body": {
                    "error": "SQS Error",
                    "message": "Failed to send message to SQS queue",
                    "details": str(e),
                },
            }

    def send_message_batch(self, message_body_list):
        """
        Send multiple messages to the SQS queue

        Args:
            message_body_list (list[dict]): List of messages to send

        Returns:
            dict: Response with statusCode and SQS message details
        """
        try:
            collected_responses = {"Successful": [], "Failed": []}

            repacked_messages = [
                {"Id": str(i), "MessageBody": json.dumps(message_body)}
                for i, message_body in enumerate(message_body_list)
            ]

            for batch in batched(repacked_messages, 10):
                # the SQS API only allows up to 10 messages per batch
                response = self.sqs.send_message_batch(QueueUrl=self.queue_url, Entries=list(batch))
                collected_responses["Successful"].extend(response.get("Successful", []))
                collected_responses["Failed"].extend(response.get("Failed", []))

            if len(collected_responses["Failed"]) > 0:
                return {
                    "statusCode": 500,
                    "body": {
                        "error": "SQS Error",
                        "message": f'{len(collected_responses["Failed"])} of {len(message_body_list)} messages failed to send to SQS queue',
                        "details": collected_responses,
                    },
                }
            else:
                return {
                    "statusCode": 200,
                    "body": {
                        "message": "All messages sent to SQS queue",
                        "sqs_message_ids": collected_responses,
                    },
                }

        except Exception as e:
            return {
                "statusCode": 500,
                "body": {
                    "error": "SQS Error",
                    "message": "Failed to send message to SQS queue",
                    "details": str(e),
                },
            }

    @staticmethod
    def parse_event(event):
        """
        Parse Lambda event and return the body

        Args:
            event (dict): Lambda event (SQS or direct)

        Returns:
            dict: Parsed message body or original event if direct invocation
        """
        if "Records" in event:
            # SQS event - return the parsed message body
            message_body = event["Records"][0]["body"]
            return json.loads(message_body)
        else:
            # Direct invocation - return the event as-is
            return event
