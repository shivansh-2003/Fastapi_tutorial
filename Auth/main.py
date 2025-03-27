from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
import auth
from schemas import Token, UserCreate, UserPublic
from database import db

# Initialize FastAPI app
app = FastAPI(title="FastAPI JWT Auth with Supabase")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/users/", response_model=UserPublic)
async def create_user(user_data: UserCreate):
    # Check if user already exists
    if await db.get_user(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    hashed_password = auth.get_password_hash(user_data.password)
    user = await db.create_user(
        user_data.username,
        hashed_password,
        user_data.full_name,
        user_data.email
    )
    
    return UserPublic(
        username=user["username"],
        full_name=user["full_name"],
        email=user["email"],
        disabled=user["disabled"]
    )

@app.get("/users/me", response_model=UserPublic)
async def read_users_me(current_user: UserPublic = Depends(auth.get_current_active_user)):
    return current_user

@app.get("/protected-resource/")
async def protected_resource(current_user: UserPublic = Depends(auth.get_current_active_user)):
    return {
        "message": f"Hello, {current_user.full_name}! This is a protected resource.",
        "data": "This data is only visible to authenticated users."
    }
@app.get("/test")
async def test_endpoint():
    return {"message": "API is working"}