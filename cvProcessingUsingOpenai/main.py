import os
import logging
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from dotenv import load_dotenv
import openai
from sqs_handler import check_sqs_queue_availability

# Load environment variables from .env file
load_dotenv()

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

# Initialize FastAPI app using environment values
app = FastAPI(
    title=os.getenv("APP_TITLE", "Default App Title"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    debug=os.getenv("IS_DEBUG", "True") == "True",  # Convert to boolean
    description=os.getenv("DESCRIPTION", "No description available")
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG  # Change to INFO for less verbosity
)
logger = logging.getLogger(__name__)

# Use SQS URLs from config
queue_url = os.getenv("QUEUE_URL")
response_queue_url = os.getenv("RESPONSE_QUEUE_URL")

@app.on_event("startup")
@repeat_every(seconds=10)  # Check every 10 seconds
async def periodic_task():
    """
    Periodically checks the SQS queue for new messages and processes them.
    """
    await check_sqs_queue_availability()

# Define a basic route for the FastAPI app
@app.get("/")
async def index():
    """
    Root endpoint of the API.
    Returns a welcome message.
    """
    return {"message": "Welcome to AIDIPH AI API"}


