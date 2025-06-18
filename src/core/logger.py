import logging
from logging.handlers import RotatingFileHandler
import os
from src.core.constant import APP_NAME

LOG_FILE = "logs/app.log"
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(APP_NAME)
