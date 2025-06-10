import functools
import hashlib
import time
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


def redis_cache(expiration: int = 3600):
    """Decorator to cache function results in Redis"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"cache:{func.__name__}:{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
            
            # Try to get cached result
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result, default=str))
            
            return result
        return wrapper
    return decorator

# Example of using the caching decorator
@app.get("/expensive-operation/{n}")
@redis_cache(expiration=300)  # Cache for 5 minutes
async def expensive_operation(n: int):
    """Simulate an expensive operation"""
    await asyncio.sleep(2)  # Simulate delay
    result = sum(i * i for i in range(n))
    return {
        "input": n,
        "result": result,
        "computed_at": time.time(),
        "message": "This was computed (not cached)"
    }
