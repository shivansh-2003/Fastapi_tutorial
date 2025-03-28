import os
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import db
from schemas import TokenData, UserPublic
from models import UserInDB
from utils import generate_reset_token
from email import send_password_reset_email

# Load environment variables
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Security utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_user(username: str):
    user_dict = await db.get_user(username)
    if user_dict:
        return UserInDB(**user_dict)
    return None

async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return UserPublic(
        username=current_user.username,
        full_name=current_user.full_name,
        email=current_user.email,
        verified=current_user.verified,
        disabled=current_user.disabled
    )

async def get_current_verified_user(current_user: UserPublic = Depends(get_current_active_user)):
    if not current_user.verified:
        raise HTTPException(status_code=400, detail="Email not verified")
    return current_user

async def request_password_reset(email: str) -> bool:
    """Request a password reset for the given email"""
    user = await db.get_user_by_email(email)
    if not user:
        # Don't reveal that the email doesn't exist
        return True
    
    reset_token = generate_reset_token()
    success = await db.store_reset_token(email, reset_token)
    
    if success:
        # Send password reset email
        send_password_reset_email(email, reset_token)
    
    return success

async def reset_password(reset_token: str, new_password: str) -> bool:
    """Reset a user's password using a reset token"""
    user_id = await db.validate_reset_token(reset_token)
    if not user_id:
        return False
    
    hashed_password = get_password_hash(new_password)
    return await db.update_password(user_id, hashed_password)
