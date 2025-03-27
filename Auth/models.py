from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    disabled: Optional[bool] = False
    created_at: Optional[datetime] = None

class UserInDB(User):
    hashed_password: str