from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import json
import uuid
from typing import Optional
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="Redis FastAPI Demo", version="1.0.0")

# Initialize Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Pydantic models
class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    age: int

class CacheItem(BaseModel):
    key: str
    value: str
    ttl: Optional[int] = 3600  # Time to live in seconds
# Get a value by key
@app.get("/cache/get/{key}")
async def get_cache(key: str):
    try:
        value = redis_client.get(key)
        if value is None:
            raise HTTPException(status_code=404, detail="Key not found")
        return {"key": key, "value": value, "ttl": redis_client.ttl(key)}
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/users/", response_model=User)
async def create_user(user: User):
    try:
        user_id = str(uuid.uuid4())
        user.id = user_id
        
        # Store user data as JSON
        user_key = f"user:{user_id}"
        redis_client.set(user_key, user.json())
        
        # Add user ID to a set for easy retrieval
        redis_client.sadd("users", user_id)
        
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get user by ID
@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    try:
        user_key = f"user:{user_id}"
        user_data = redis_client.get(user_key)
        
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return User.parse_raw(user_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid user data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all users
@app.get("/users/")
async def get_all_users():
    try:
        user_ids = redis_client.smembers("users")
        users = []
        
        for user_id in user_ids:
            user_key = f"user:{user_id}"
            user_data = redis_client.get(user_key)
            if user_data:
                users.append(User.parse_raw(user_data))
        
        return {"users": users, "count": len(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update user
@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: User):
    try:
        user_key = f"user:{user_id}"
        
        # Check if user exists
        if not redis_client.exists(user_key):
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user data
        user_update.id = user_id
        redis_client.set(user_key, user_update.json())
        
        return user_update
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete user
@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    try:
        user_key = f"user:{user_id}"
        
        # Delete user data and remove from set
        deleted = redis_client.delete(user_key)
        redis_client.srem("users", user_id)
        
        if deleted == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": f"User {user_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))