from fastapi import APIRouter, HTTPException
from datetime import datetime
from models.user_model import UserCreate
from app import users
from passlib.context import CryptContext
from pydantic import BaseModel
from utils.jwt_handler import create_token
from fastapi import Depends
from utils.auth_dependency import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -------- LOGIN MODEL --------
class LoginData(BaseModel):
    email: str
    password: str

@router.get("/me")
def get_me(user_id: str = Depends(get_current_user)):

    user = users.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(404, "User not found")

    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "bio": user.get("bio",""),
        "avatar": user.get("avatar","/avatar1.png")
    }
@router.put("/me")
def update_me(payload: dict, user_id: str = Depends(get_current_user)):

    users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": payload}
    )

    return {"status":"updated"}

# -------- LOGIN --------
@router.post("/login")
def login(payload: LoginData):

    user = users.find_one({"email": payload.email})

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not pwd.verify(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # 🔥 CREATE TOKEN HERE (inside function)
    token = create_token({"user_id": str(user["_id"])})

    return {
        "access_token": token,
        "user": {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"]
        }
    }


# -------- REGISTER --------
@router.post("/register")
def register(payload: UserCreate):

    if users.find_one({"email": payload.email}):
        raise HTTPException(400, "User already exists")

    user = {
      "username": payload.username,
    "email": payload.email,
    "password_hash": pwd.hash(payload.password[:72]),

    "bio": "",
    "avatar": "/avatar1.png",
    "github_username": None,

    "created_at": datetime.utcnow()
    }

    result = users.insert_one(user)

    return {"user_id": str(result.inserted_id)}
