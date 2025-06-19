from fastapi import HTTPException
from starlette import status
from src.models.user import User, BaseUser, UpdateUser
from src.db.collections import users_collection
from src.schema.user_schema import user_schema
from typing import Optional
from datetime import datetime, timezone
from src.utils.converters.convert_to_object_id import convert_to_object_id
from src.core.config import ENV_VARS


async def create_user(data: BaseUser) -> User:
    existing_user = await get_user_by_email(data.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email: {data.email} already exists",
        )

    new_user = data.model_dump()

    now = datetime.now(timezone.utc)
    new_user["updatedAt"] = now
    new_user["createdAt"] = now

    response = await users_collection.insert_one(new_user)
    new_user["_id"] = response.inserted_id

    return user_schema(new_user)


async def get_user_by_email(email: str) -> Optional[User]:
    user = await users_collection.find_one({"email": email})

    if not user:
        return None

    return user_schema(user)


async def get_user_by_id(id: str) -> Optional[User]:
    user_id = convert_to_object_id(id)
    user = await users_collection.find_one({"_id": user_id})

    if not user:
        return None

    return user_schema(user)


async def get_current_user() -> Optional[User]:
    user = await get_user_by_id(ENV_VARS["ADMIN_USER_ID"])

    if not user:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


async def update_user(user_id: str, update_data: UpdateUser) -> User:
    user = await get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {user_id} not found",
        )

    update_user_obj = update_data.model_dump(exclude_unset=True)
    update_user_obj["updatedAt"] = datetime.now(timezone.utc)

    await users_collection.update_one(
        {"_id": convert_to_object_id(user_id)},
        {"$set": update_data.model_dump(exclude_unset=True)},
    )

    updated_user = await get_user_by_id(user_id)

    return updated_user


async def delete_user(user_id: str) -> None:
    user = await get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {user_id} not found",
        )

    response = await users_collection.delete_one({"_id": convert_to_object_id(user_id)})

    if response.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete user with id: {user_id}",
        )
