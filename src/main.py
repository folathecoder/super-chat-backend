from fastapi import FastAPI
from src.api.v1.endpoints.health import health_router
from src.api.v1.endpoints.user import user_router
from src.db.mongo import is_mongo_connected, client
from src.core.config import validate_env_vars
from src.core.logger import logger
from src.core.constant import APP_NAME
from contextlib import asynccontextmanager

version = "v1"
base_url = f"/api/{version}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        is_mongo_connected()
        validate_env_vars()

        logger.info(f"Starting {APP_NAME} application...")

        yield
    except Exception as e:
        logger.error("Application failed to connect to MongoDB: %s", e)

        raise
    finally:
        logger.info("Shutting down application...")

        await client.close()


app = FastAPI(lifespan=lifespan)
app.include_router(health_router, prefix=f"{base_url}/health", tags=["Health"])
app.include_router(user_router, prefix=f"{base_url}/user", tags=["User"])
