import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from ..services.storage import GameStorage
from ..services.websocket import ConnectionManager

def setup_websocket_routes(app: FastAPI, storage: GameStorage, manager: ConnectionManager):
    @app.websocket("/ws/{user_id}")
    async def websocket_endpoint(websocket: WebSocket, user_id: str):
        connection_id = await manager.connect(websocket, user_id)


        if user_id in storage.users:
            storage.users[user_id]['is_online'] = True
            storage.save_data()

        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)

                if message['type'] == 'mouse_position':
                    storage.update_mouse_position(
                        user_id, 
                        message['x'], 
                        message['y']
                    )
        except WebSocketDisconnect:
            manager.disconnect(connection_id, user_id)


            if user_id in storage.users:
                storage.users[user_id]['is_online'] = False
                storage.save_data()
