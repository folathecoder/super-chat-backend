from dotenv import load_dotenv
from src.core.logger import logger
import os

load_dotenv()

ENV_VARS = {"MONGO_URI": os.getenv("MONGO_URI"), "MONGO_DB": os.getenv("MONGO_DB")}


def are_env_vars_loaded() -> bool:
    missing = [key for key, val in ENV_VARS.items() if not val]

    if missing:
        logger.error(f"Missing the following environment variables: {missing}")
        return False

    return True


def validate_env_vars():
    if not are_env_vars_loaded():
        raise EnvironmentError("One or more required environment variables are missing")
