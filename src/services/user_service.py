from fastapi import HTTPException
from starlette import status
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from src.models.user import User, BaseUser, UpdateUser
from src.db.collections import users_collection
from src.schema.user_schema import user_schema
from src.utils.converters.convert_to_object_id import convert_to_object_id
from src.core.config import ENV_VARS
from src.llm.prompts.template.user_profile_template import user_profile_template


async def create_user(data: BaseUser) -> User:
    """
    Create a new user in the database.

    Args:
        data (BaseUser): Data required to create the user.

    Returns:
        User: The created user object.

    Raises:
        HTTPException: If a user with the same email already exists.
    """
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
    """
    Retrieve a user by their email.

    Args:
        email (str): Email of the user.

    Returns:
        Optional[User]: User object if found, else None.
    """
    user = await users_collection.find_one({"email": email})
    if not user:
        return None
    return user_schema(user)


async def get_user_by_id(id: str) -> Optional[User]:
    """
    Retrieve a user by their ID.

    Args:
        id (str): User's ID.

    Returns:
        Optional[User]: User object if found, else None.
    """
    user_id = convert_to_object_id(id)
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        return None
    return user_schema(user)


async def get_current_user() -> Optional[User]:
    """
    Get the current user from environment config.

    Returns:
        Optional[User]: The current user object.

    Raises:
        HTTPException: If current user is not found.
    """
    user = await get_user_by_id(ENV_VARS["ADMIN_USER_ID"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


async def update_user(user_id: str, update_data: UpdateUser) -> User:
    """
    Update user details.

    Args:
        user_id (str): ID of the user to update.
        update_data (UpdateUser): Data to update.

    Returns:
        User: Updated user object.

    Raises:
        HTTPException: If user does not exist.
    """
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
        {"$set": update_user_obj},
    )

    updated_user = await get_user_by_id(user_id)
    return updated_user


async def delete_user(user_id: str) -> None:
    """
    Delete a user by ID.

    Args:
        user_id (str): ID of the user to delete.

    Raises:
        HTTPException: If user does not exist or deletion fails.
    """
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


async def user_profile_context() -> str:
    """
    Get a user's profile and format it into a descriptive string
    that can be passed as context to an LLM.

    Returns:
        str: Overview of the user based on their profile
    """

    user = await get_current_user()

    first_name: str = user.get("firstName", "Unknown")
    last_name: str = user.get("lastName", "User")
    occupation: str = user.get("occupation", "Not specified")
    industry: str = user.get("industry", "Not specified")
    interests: str = ", ".join(user.get("interests", []))
    goals: str = ", ".join(user.get("goals", []))
    expertise_areas: str = ", ".join(user.get("expertiseAreas", []))

    user_data: Dict[str, str] = {
        "firstName": first_name,
        "lastName": last_name,
        "occupation": occupation,
        "industry": industry,
        "interests": interests,
        "goals": goals,
        "expertiseAreas": expertise_areas,
    }

    return user_profile_template.format(**user_data)
