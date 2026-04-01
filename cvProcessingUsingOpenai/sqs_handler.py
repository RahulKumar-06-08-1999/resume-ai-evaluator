import logging
from botocore.exceptions import BotoCoreError, ClientError
import boto3
from candidate_processor import process_files_from_sqs
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize SQS client
sqs = boto3.client(
    "sqs",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

async def check_sqs_queue_availability():
    """
    Periodically checks the SQS queue for messages and processes files directly.
    """
    logger.debug(f"QUEUE_URL: {os.getenv('QUEUE_URL')}")
    logger.debug(f"RESPONSE_QUEUE_URL: {os.getenv('RESPONSE_QUEUE_URL')}")
    
    try:
        response = sqs.receive_message(
            QueueUrl=os.getenv("QUEUE_URL"),
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
            VisibilityTimeout=30
        )
        logger.debug(f"SQS Response: {response}")

        if "Messages" in response:
            logger.info("Messages are available in the SQS queue.")
            
            for message in response["Messages"]:
                message_body = json.loads(message["Body"])
                await process_files_from_sqs(message_body)  # Pass message body directly
                
                # Delete the message from the SQS queue
                sqs.delete_message(
                    QueueUrl=os.getenv("QUEUE_URL"),
                    ReceiptHandle=message["ReceiptHandle"]
                )
                logger.info(f"Message {message['MessageId']} deleted from SQS queue.")
        else:
            logger.info("No messages in the SQS queue.")
    except (BotoCoreError, ClientError) as e:
        logger.error(f"Error checking SQS queue availability: {str(e)}")
