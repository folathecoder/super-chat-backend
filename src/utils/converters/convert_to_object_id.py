from bson import ObjectId
from fastapi import HTTPException
from starlette import status


def convert_to_object_id(value: str) -> ObjectId:
    """
    Convert a string value to a BSON ObjectId.

    Args:
        value (str): The string representation of an ObjectId.

    Returns:
        ObjectId: The corresponding BSON ObjectId.

    Raises:
        HTTPException: Raises 400 BAD REQUEST if the value is not a valid ObjectId.
    """
    try:
        return ObjectId(value)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid objectId format: {str(e)}",
        )
