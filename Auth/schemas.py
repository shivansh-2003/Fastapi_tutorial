from pydantic import BaseModel, EmailStr, Field
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
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class UserPublic(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    verified: bool
    disabled: Optional[bool] = None

class EmailVerification(BaseModel):
    verification_code: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    reset_token: str
    new_password: str = Field(..., min_length=8)

class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
