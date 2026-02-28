from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class User(BaseModel):

    id: str | None = None

    username: str
    email: EmailStr

    bio: str | None = ""
    avatar: str | None = "/avatar1.png"

    github_username: str | None = None

    created_at: datetime = datetime.utcnow()
