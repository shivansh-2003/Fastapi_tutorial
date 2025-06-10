from datetime import datetime, timedelta
from pydantic import BaseModel
import redis
import json
import uuid
from typing import Optional
import uvicorn
from fastapi import FastAPI, HTTPException

# Initialize FastAPI app
app = FastAPI(title="Redis FastAPI Demo", version="1.0.0")

# Initialize Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
class SessionManager:
    def __init__(self, redis_client, default_ttl=3600):
        self.redis = redis_client
        self.default_ttl = default_ttl
    
    def create_session(self, user_id: str, data: dict = None) -> str:
        session_id = str(uuid.uuid4())
        session_data = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "data": data or {}
        }
        
        session_key = f"session:{session_id}"
        self.redis.setex(session_key, self.default_ttl, json.dumps(session_data))
        
        return session_id
    
    def get_session(self, session_id: str) -> dict:
        session_key = f"session:{session_id}"
        session_data = self.redis.get(session_key)
        
        if not session_data:
            return None
        
        return json.loads(session_data)
    
    def update_session(self, session_id: str, data: dict):
        session = self.get_session(session_id)
        if session:
            session["data"].update(data)
            session_key = f"session:{session_id}"
            self.redis.setex(session_key, self.default_ttl, json.dumps(session))
    
    def delete_session(self, session_id: str):
        session_key = f"session:{session_id}"
        self.redis.delete(session_key)

# Initialize session manager
session_manager = SessionManager(redis_client)

@app.post("/sessions/")
async def create_session(user_id: str):
    session_id = session_manager.create_session(user_id)
    return {"session_id": session_id}

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    session_manager.delete_session(session_id)
    return {"message": "Session deleted"}