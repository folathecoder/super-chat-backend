from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import ENV_VARS
from src.core.logger import logger

# Initialize async MongoDB client using URI from environment variables
client = AsyncIOMotorClient(ENV_VARS["MONGO_URI"])

# Select the database by name from environment variables
db = client[ENV_VARS["MONGO_DB"]]


def get_db():
    """
    Retrieve the MongoDB database instance.

    Returns:
        AsyncIOMotorDatabase: The MongoDB database object.
    """
    return db


def is_mongo_connected():
    """
    Check the MongoDB connection by sending a ping command.

    Returns:
        bool: True if connection is successful, False otherwise.
    """
    try:
        client.admin.command("ping")
        logger.info("Application successfully connected to MongoDB!")
        return True
    except Exception as e:
        logger.error("Application failed to connect to MongoDB", e)
        return False
