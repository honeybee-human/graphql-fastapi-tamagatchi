import json
import uuid
from typing import Dict, Callable, Any, Coroutine
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, str] = {}
        self.subscription_handlers: Dict[int, Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        self.user_connections[user_id] = connection_id
        return connection_id

    def disconnect(self, connection_id: str, user_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    def register_subscription_handler(self, subscription_id: int, handler: Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]):
        self.subscription_handlers[subscription_id] = handler

    def unregister_subscription_handler(self, subscription_id: int):
        if subscription_id in self.subscription_handlers:
            del self.subscription_handlers[subscription_id]

    async def broadcast(self, message: dict):
        # First, notify all subscription handlers
        for handler in self.subscription_handlers.values():
            try:
                await handler(message)
            except Exception as e:
                print(f"Error in subscription handler: {e}")

        # Then, send to all WebSocket connections
        disconnected = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except:
                disconnected.append(connection_id)

        for conn_id in disconnected:
            if conn_id in self.active_connections:
                del self.active_connections[conn_id]

    async def send_to_user(self, user_id: str, message: dict):
        connection_id = self.user_connections.get(user_id)
        if connection_id and connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_text(json.dumps(message))
            except:
                self.disconnect(connection_id, user_id)
