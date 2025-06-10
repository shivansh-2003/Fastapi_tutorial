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

@app.get("/")
async def root():
    return {"message": "FastAPI + Redis Tutorial"}

# Test Redis connection
@app.get("/redis/ping")
async def ping_redis():
    try:
        response = redis_client.ping()
        return {"redis_status": "connected", "ping": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection failed: {str(e)}")

# Set a key-value pair with optional TTL
@app.post("/cache/set")
async def set_cache(item: CacheItem):
    try:
        if item.ttl:
            redis_client.setex(item.key, item.ttl, item.value)
        else:
            redis_client.set(item.key, item.value)
        return {"message": f"Key '{item.key}' set successfully", "ttl": item.ttl}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

# Delete a key
@app.delete("/cache/delete/{key}")
async def delete_cache(key: str):
    try:
        result = redis_client.delete(key)
        if result == 0:
            raise HTTPException(status_code=404, detail="Key not found")
        return {"message": f"Key '{key}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    