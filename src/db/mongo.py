from pymongo import MongoClient
from src.core.config import ENV_VARS
from src.core.logger import logger

client = MongoClient(ENV_VARS["MONGO_URI"])
db = client[ENV_VARS["MONGO_DB"]]

def get_db():
  return db

def is_mongo_connected():
  try:
    client.admin.command("ping")
    logger.info("Application successfully connected to MongoDB!")
    return True
  except Exception as e:
    logger.error("Application failed to connect to MongoDB", e)
    return False