from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from typing import List

import auth
from schemas import Token, UserCreate, UserPublic, EmailVerification, PasswordResetRequest, PasswordReset, ChangePassword, UserUpdate
from database import db
from email import send_verification_email

# Initialize FastAPI app
app = FastAPI(title="FastAPI Login/Signup System with Supabase")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# User registration and profile
@app.post("/register", response_model=UserPublic)
async def register_user(background_tasks: BackgroundTasks, user_data: UserCreate):
    # Check if user already exists
    if await db.get_user(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if await db.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = auth.get_password_hash(user_data.password)
    user = await db.create_user(
        user_data.username,
        hashed_password,
        user_data.full_name,
        user_data.email
    )
    
    # Send verification email in the background
    background_tasks.add_task(
        send_verification_email,
        user_data.email,
        user["verification_code"]
    )
    
    return UserPublic(
        username=user["username"],
        full_name=user["full_name"],
        email=user["email"],
        verified=user["verified"],
        disabled=user["disabled"]
    )

@app.get("/users/me", response_model=UserPublic)
async def read_users_me(current_user: UserPublic = Depends(auth.get_current_active_user)):
    return current_user

@app.put("/users/me", response_model=UserPublic)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: UserPublic = Depends(auth.get_current_active_user)
):
    update_data = user_data.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # If email is being updated, set verified to False and generate new verification code
    if "email" in update_data and update_data["email"] != current_user.email:
        # Check if email already exists
        if await db.get_user_by_email(update_data["email"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        verification_code = auth.generate_verification_code()
        update_data["verified"] = False
        update_data["verification_code"] = verification_code
        
        # Send verification email
        send_verification_email(update_data["email"], verification_code)
    
    updated_user = await db.update_user(current_user.username, update_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
    
    return UserPublic(
        username=updated_user["username"],
        full_name=updated_user["full_name"],
        email=updated_user["email"],
        verified=updated_user["verified"],
        disabled=updated_user["disabled"]
    )

@app.post("/verify-email", response_model=dict)
async def verify_email(verification_data: EmailVerification):
    success = await db.verify_user(verification_data.verification_code)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    return {"message": "Email verified successfully"}

@app.post("/request-password-reset", response_model=dict)
async def request_password_reset_endpoint(reset_request: PasswordResetRequest):
    await auth.request_password_reset(reset_request.email)
    
    # Always return success to prevent email enumeration
    return {"message": "If your email is registered, you will receive a password reset link"}

@app.post("/reset-password", response_model=dict)
async def reset_password_endpoint(reset_data: PasswordReset):
    success = await auth.reset_password(reset_data.reset_token, reset_data.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {"message": "Password reset successfully"}

@app.post("/change-password", response_model=dict)
async def change_password(
    password_data: ChangePassword,
    current_user: UserPublic = Depends(auth.get_current_verified_user)
):
    # Verify current password
    user = await auth.get_user(current_user.username)
    if not auth.verify_password(password_data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    hashed_password = auth.get_password_hash(password_data.new_password)
    success = await db.update_user(current_user.username, {"hashed_password": hashed_password})
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
    
    return {"message": "Password changed successfully"}

# Protected resource endpoint
@app.get("/protected-resource")
async def protected_resource(current_user: UserPublic = Depends(auth.get_current_verified_user)):
    return {
        "message": f"Hello, {current_user.full_name}! This is a protected resource.",
        "data": "This data is only visible to verified users."
    }