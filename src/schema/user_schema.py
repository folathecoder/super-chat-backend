from src.models.user import User


def user_schema(user: User):
    return {
        "id": str(user["_id"]),
        "firstName": user["firstName"],
        "lastName": user["lastName"],
        "email": user["email"],
        "occupation": user.get("occupation"),
        "industry": user.get("industry"),
        "interests": user.get("interests", []),
        "goals": user.get("goals", []),
        "expertiseAreas": user.get("expertiseAreas", []),
        "createdAt": user.get("createdAt"),
        "updatedAt": user.get("updatedAt"),
    }
