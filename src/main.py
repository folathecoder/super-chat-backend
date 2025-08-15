from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.endpoints.health import health_router
from src.api.v1.endpoints.user import user_router
from src.api.v1.endpoints.conversation import conversation_router
from src.api.v1.endpoints.message import messages_router
from src.api.v1.endpoints.newsletter import newsletter_router
from src.db.mongo import is_mongo_connected, client
from src.core.config import validate_env_vars
from src.core.logger import logger
from src.core.constant import APP_NAME
from src.core.server.socket_server import socket_app
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

version = "v1"
base_url = f"/api/{version}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown logic for the FastAPI app.
    """
    try:
        validate_env_vars()
        is_mongo_connected()
        logger.info(f"Starting {APP_NAME} application...")
        yield
    except Exception as e:
        logger.error("Application failed to connect to MongoDB: %s", e)
        raise
    finally:
        logger.info("Shutting down application...")
        try:
            if client:
                await client.close()
                logger.info("MongoDB connection closed.")
        except Exception as e:
            logger.warning(f"Error while closing MongoDB client: {e}")


# Create FastAPI app for HTTP routes only
app = FastAPI(
    title=APP_NAME,
    description="Super Chat API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include HTTP routers
app.include_router(health_router, prefix=f"{base_url}/health", tags=["Health"])
app.include_router(user_router, prefix=f"{base_url}/users", tags=["User"])
app.include_router(
    conversation_router, prefix=f"{base_url}/conversations", tags=["Conversation"]
)
app.include_router(messages_router, prefix=f"{base_url}/messages", tags=["Message"])
app.include_router(
    newsletter_router, prefix=f"{base_url}/newsletters", tags=["Newsletter"]
)


app.mount("/socket.io", socket_app)
