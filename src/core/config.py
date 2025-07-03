from dotenv import load_dotenv
from src.core.logger import logger
import os

load_dotenv()

ENV_VARS = {
    "MONGO_URI": os.getenv("MONGO_URI"),
    "MONGO_DB": os.getenv("MONGO_DB"),
    "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
    "ADMIN_USER_ID": os.getenv("ADMIN_USER_ID"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "LANGSMITH_TRACING": os.getenv("LANGSMITH_TRACING"),
    "LANGSMITH_ENDPOINT": os.getenv("LANGSMITH_ENDPOINT"),
    "LANGSMITH_API_KEY": os.getenv("LANGSMITH_API_KEY"),
    "LANGCHAIN_API_KEY": os.getenv("LANGCHAIN_API_KEY"),
    "LANGSMITH_PROJECT": os.getenv("LANGSMITH_PROJECT"),
    "AWS_S3_BUCKET_NAME": os.getenv("AWS_S3_BUCKET_NAME"),
}


def are_env_vars_loaded() -> bool:
    """
    Check if all required environment variables are set.

    Returns:
        bool: True if all required variables are present, False otherwise.
    """
    missing = [key for key, val in ENV_VARS.items() if not val]

    if missing:
        logger.error(f"Missing the following environment variables: {missing}")
        return False

    return True


def validate_env_vars():
    """
    Validate environment variables and raise an error if any are missing.

    Raises:
        EnvironmentError: If one or more required environment variables are missing.
    """
    if not are_env_vars_loaded():
        raise EnvironmentError("One or more required environment variables are missing")
