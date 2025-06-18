from bson import ObjectId
from fastapi import HTTPException
from starlette import status


def convert_to_object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid objectId format: {str(e)}",
        )
