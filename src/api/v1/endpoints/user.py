from fastapi import APIRouter, HTTPException
from starlette import status
from src.models.user import User, BaseUser, UpdateUser
from src.services.user_service import (
    create_user,
    get_user_by_id,
    update_user,
    delete_user,
)

user_router = APIRouter()


@user_router.post("/", status_code=status.HTTP_201_CREATED, response_model=User)
async def create_user_endpoint(data: BaseUser):
    try:
        return await create_user(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User not created: {str(e)}",
        )


@user_router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=User)
async def get_user_endpoint(user_id: str):
    try:
        return await get_user_by_id(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {user_id} not found: {str(e)}",
        )


@user_router.patch("/{user_id}", status_code=status.HTTP_200_OK, response_model=User)
async def update_user_endpoint(user_id: str, data: UpdateUser):
    try:
        return await update_user(user_id, data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with id: {user_id} not updated: {str(e)}",
        )


@user_router.delete(
    "/{user_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None
)
async def delete_user_endpoint(user_id: str):
    try:
        return await delete_user(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with id: {user_id} was not deleted: {str(e)}",
        )
