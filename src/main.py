from fastapi import FastAPI, APIRouter

router = APIRouter()

@router.get("/")
def home():
    return {
      "firstName": "James",
      "lastName": "Harden"
    }

app = FastAPI()
app.include_router(router)