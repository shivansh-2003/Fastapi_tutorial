from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    disabled: Optional[bool] = None