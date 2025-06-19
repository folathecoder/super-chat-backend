from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette import status
from src.db.mongo import is_mongo_connected
from src.core.config import are_env_vars_loaded

health_router = APIRouter()


@health_router.get("/", status_code=status.HTTP_200_OK)
async def health_endpoint():
    return {"status": "working"}


@health_router.get("/deep", status_code=status.HTTP_200_OK)
async def deep_health_check_endpoint():
    checks = {
        "mongo_connected": is_mongo_connected(),
        "env_vars_loaded": are_env_vars_loaded(),
    }

    status = all(checks.values())

    if status:
        return {"status": "healthy", "checks": checks}
    else:
        return JSONResponse(
            status_code=503, content={"status": "unhealthy", "checks": checks}
        )
