from src.models.user import User


def user_schema(user: User):
    return {
        "firstName": user["firstName"],
        "lastName": user["lastName"],
        "email": user["email"],
        "id": str(user["_id"]),
    }
