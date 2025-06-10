import asyncio
from fastapi import WebSocket, WebSocketDisconnect
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

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Publish message to Redis
            redis_client.publish("chat", data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Redis subscriber (run this in background)
async def redis_subscriber():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("chat")
    
    for message in pubsub.listen():
        if message["type"] == "message":
            await manager.broadcast(message["data"])

@app.post("/broadcast")
async def broadcast_message(message: str):
    redis_client.publish("chat", message)
    return {"message": "Message broadcasted"}