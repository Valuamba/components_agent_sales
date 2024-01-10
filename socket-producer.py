# app.py

from fastapi import FastAPI, WebSocket, APIRouter, HTTPException, WebSocketDisconnect
from typing import List
import json

app = FastAPI()
router = APIRouter()
connections: List[WebSocket] = []

from pydantic import BaseModel

class EmailEvent(BaseModel):
    type: str
    subject: str
    body: str

class CustomerServiceEvent(BaseModel):
    type: str
    tool: str
    sources: str
    reasoning_flow: str
    metadata: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: str):
        for connection in self.active_connections:
            await connection.send_text(data)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Just keep the connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/send_email_event/")
async def send_email_event(event: EmailEvent):
    await manager.broadcast(event.json())
    return {"message": "Email event sent"}

@app.post("/send_customer_service_event/")
async def send_customer_service_event(event: CustomerServiceEvent):
    await manager.broadcast(event.json())
    return {"message": "Customer service event sent"}

app.include_router(router)
