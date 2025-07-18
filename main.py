from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from datetime import datetime, timedelta
import asyncio
from typing import Optional, List, Dict, AsyncGenerator
import json
import os
import uuid
import random
import math
from jose import JWTError, jwt
from passlib.context import CryptContext

# Security
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# User and Tamagotchi models
@strawberry.type
class User:
    id: str
    username: str
    created_at: str
    mouse_x: float = 0.0
    mouse_y: float = 0.0
    is_online: bool = False

@strawberry.type
class Position:
    x: float
    y: float
    direction: float  # angle in radians
    speed: float = 1.0

@strawberry.type
class Tamagotchi:
    id: str
    name: str
    owner_id: str
    happiness: int
    hunger: int
    energy: int
    health: int
    age: int
    last_fed: str
    last_played: str
    last_slept: str
    created_at: str
    is_alive: bool
    status: str
    position: Position
    emoji: str

@strawberry.type
class MousePosition:
    user_id: str
    username: str
    x: float
    y: float
    timestamp: str

# Input types
@strawberry.input
class CreateUserInput:
    username: str
    password: str

@strawberry.input
class LoginInput:
    username: str
    password: str

@strawberry.input
class CreateTamagotchiInput:
    name: str

@strawberry.input
class ActionInput:
    tamagotchi_id: str

@strawberry.input
class MousePositionInput:
    x: float
    y: float

@strawberry.type
class AuthPayload:
    token: str
    user: User

# Connection manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, str] = {}  # user_id -> connection_id
    
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
    
    async def broadcast(self, message: dict):
        disconnected = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except:
                disconnected.append(connection_id)
        
        # Clean up disconnected connections
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

manager = ConnectionManager()

# Enhanced storage with multi-user support
class GameStorage:
    def __init__(self):
        self.users: Dict[str, dict] = {}
        self.tamagotchis: Dict[str, dict] = {}
        self.mouse_positions: Dict[str, dict] = {}
        self.load_data()
        self._tasks_started = False
    
    async def start_background_tasks(self):
        """Start background tasks - call this when the app starts"""
        if not self._tasks_started:
            asyncio.create_task(self.update_stats_loop())
            asyncio.create_task(self.update_positions_loop())
            self._tasks_started = True

    def save_data(self):
        data = {
            'users': self.users,
            'tamagotchis': self.tamagotchis,
            'mouse_positions': self.mouse_positions
        }
        with open('game_data.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_data(self):
        if os.path.exists('game_data.json'):
            with open('game_data.json', 'r') as f:
                data = json.load(f)
                self.users = data.get('users', {})
                self.tamagotchis = data.get('tamagotchis', {})
                self.mouse_positions = data.get('mouse_positions', {})
    
    def create_user(self, username: str, password: str) -> User:
        # Check if username exists
        for user_data in self.users.values():
            if user_data['username'] == username:
                raise ValueError("Username already exists")
        
        user_id = str(uuid.uuid4())
        hashed_password = pwd_context.hash(password)
        now = datetime.now().isoformat()
        
        user_data = {
            'id': user_id,
            'username': username,
            'password': hashed_password,
            'created_at': now,
            'mouse_x': 0.0,
            'mouse_y': 0.0,
            'is_online': False
        }
        
        self.users[user_id] = user_data
        self.save_data()
        return User(**{k: v for k, v in user_data.items() if k != 'password'})
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        for user_data in self.users.values():
            if user_data['username'] == username:
                if pwd_context.verify(password, user_data['password']):
                    return User(**{k: v for k, v in user_data.items() if k != 'password'})
        return None
    
    def get_user(self, user_id: str) -> Optional[User]:
        user_data = self.users.get(user_id)
        if user_data:
            return User(**{k: v for k, v in user_data.items() if k != 'password'})
        return None
    
    def create_tamagotchi(self, name: str, owner_id: str) -> Tamagotchi:
        tamagotchi_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Random starting position
        x = random.uniform(50, 750)
        y = random.uniform(50, 550)
        direction = random.uniform(0, 2 * math.pi)
        
        # Random emoji
        emojis = ['🐱', '🐶', '🐰', '🐸', '🐧', '🐨', '🦊', '🐼']
        
        tamagotchi_data = {
            'id': tamagotchi_id,
            'name': name,
            'owner_id': owner_id,
            'happiness': 100,
            'hunger': 0,
            'energy': 100,
            'health': 100,
            'age': 0,
            'last_fed': now,
            'last_played': now,
            'last_slept': now,
            'created_at': now,
            'is_alive': True,
            'status': 'Happy',
            'position': {
                'x': x,
                'y': y,
                'direction': direction,
                'speed': 1.0
            },
            'emoji': random.choice(emojis)
        }
        
        self.tamagotchis[tamagotchi_id] = tamagotchi_data
        self.save_data()
        
        # Broadcast new tamagotchi
        asyncio.create_task(manager.broadcast({
            'type': 'tamagotchi_created',
            'tamagotchi': tamagotchi_data
        }))
        
        return self._dict_to_tamagotchi(tamagotchi_data)
    
    def _dict_to_tamagotchi(self, data: dict) -> Tamagotchi:
        position = Position(**data['position'])
        return Tamagotchi(
            id=data['id'],
            name=data['name'],
            owner_id=data['owner_id'],
            happiness=data['happiness'],
            hunger=data['hunger'],
            energy=data['energy'],
            health=data['health'],
            age=data['age'],
            last_fed=data['last_fed'],
            last_played=data['last_played'],
            last_slept=data['last_slept'],
            created_at=data['created_at'],
            is_alive=data['is_alive'],
            status=data['status'],
            position=position,
            emoji=data['emoji']
        )
    
    def get_all_tamagotchis(self) -> List[Tamagotchi]:
        return [self._dict_to_tamagotchi(data) for data in self.tamagotchis.values()]
    
    def get_user_tamagotchis(self, user_id: str) -> List[Tamagotchi]:
        return [self._dict_to_tamagotchi(data) for data in self.tamagotchis.values() 
                if data['owner_id'] == user_id]
    
    def update_mouse_position(self, user_id: str, x: float, y: float):
        if user_id in self.users:
            self.users[user_id]['mouse_x'] = x
            self.users[user_id]['mouse_y'] = y
            
            mouse_data = {
                'user_id': user_id,
                'username': self.users[user_id]['username'],
                'x': x,
                'y': y,
                'timestamp': datetime.now().isoformat()
            }
            
            self.mouse_positions[user_id] = mouse_data
            
            # Broadcast mouse position
            asyncio.create_task(manager.broadcast({
                'type': 'mouse_position',
                'data': mouse_data
            }))
    
    async def update_stats_loop(self):
        while True:
            await asyncio.sleep(1)  # Update every second
            
            updated_tamagotchis = []
            for tamagotchi_id, data in self.tamagotchis.items():
                if not data['is_alive']:
                    continue
                
                now = datetime.now()
                last_fed = datetime.fromisoformat(data['last_fed'])
                last_played = datetime.fromisoformat(data['last_played'])
                last_slept = datetime.fromisoformat(data['last_slept'])
                
                # Update stats (faster than before - per second)
                seconds_since_fed = (now - last_fed).total_seconds()
                seconds_since_played = (now - last_played).total_seconds()
                seconds_since_slept = (now - last_slept).total_seconds()
                
                # Increase hunger every 30 seconds
                if seconds_since_fed > 30:
                    data['hunger'] = min(100, data['hunger'] + 1)
                
                # Decrease happiness every 60 seconds
                if seconds_since_played > 60:
                    data['happiness'] = max(0, data['happiness'] - 1)
                
                # Decrease energy every 45 seconds
                if seconds_since_slept > 45:
                    data['energy'] = max(0, data['energy'] - 1)
                
                # Update health based on other stats
                if data['hunger'] > 80 or data['happiness'] < 20 or data['energy'] < 20:
                    data['health'] = max(0, data['health'] - 1)
                
                # Update status
                if data['health'] <= 0:
                    data['is_alive'] = False
                    data['status'] = 'Dead'
                elif data['hunger'] > 80:
                    data['status'] = 'Starving'
                elif data['energy'] < 20:
                    data['status'] = 'Tired'
                elif data['happiness'] < 30:
                    data['status'] = 'Sad'
                else:
                    data['status'] = 'Happy'
                
                # Update age (in seconds)
                created_at = datetime.fromisoformat(data['created_at'])
                data['age'] = int((now - created_at).total_seconds())
                
                updated_tamagotchis.append(self._dict_to_tamagotchi(data))
            
            if updated_tamagotchis:
                self.save_data()
                # Broadcast stats update
                await manager.broadcast({
                    'type': 'stats_update',
                    'tamagotchis': [{
                        'id': t.id,
                        'happiness': t.happiness,
                        'hunger': t.hunger,
                        'energy': t.energy,
                        'health': t.health,
                        'age': t.age,
                        'status': t.status,
                        'is_alive': t.is_alive
                    } for t in updated_tamagotchis]
                })
    
    async def update_positions_loop(self):
        while True:
            await asyncio.sleep(0.1)  # Update positions 10 times per second
            
            updated_positions = []
            for tamagotchi_id, data in self.tamagotchis.items():
                if not data['is_alive']:
                    continue
                
                pos = data['position']
                
                # Move tamagotchi
                pos['x'] += math.cos(pos['direction']) * pos['speed']
                pos['y'] += math.sin(pos['direction']) * pos['speed']
                
                # Bounce off walls
                if pos['x'] <= 0 or pos['x'] >= 800:
                    pos['direction'] = math.pi - pos['direction']
                    pos['x'] = max(0, min(800, pos['x']))
                
                if pos['y'] <= 0 or pos['y'] >= 600:
                    pos['direction'] = -pos['direction']
                    pos['y'] = max(0, min(600, pos['y']))
                
                # Randomly change direction occasionally
                if random.random() < 0.02:  # 2% chance per frame
                    pos['direction'] += random.uniform(-0.5, 0.5)
                
                updated_positions.append({
                    'id': tamagotchi_id,
                    'x': pos['x'],
                    'y': pos['y'],
                    'direction': pos['direction']
                })
            
            if updated_positions:
                # Broadcast position updates
                await manager.broadcast({
                    'type': 'position_update',
                    'positions': updated_positions
                })

storage = GameStorage()

# JWT token functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# GraphQL Schema
@strawberry.type
class Query:
    @strawberry.field
    def me(self, info) -> Optional[User]:
        # Get user from context (set by middleware)
        user_id = getattr(info.context.get("request", {}), "user_id", None)
        if user_id:
            return storage.get_user(user_id)
        return None
    
    @strawberry.field
    def all_tamagotchis(self) -> List[Tamagotchi]:
        return storage.get_all_tamagotchis()
    
    @strawberry.field
    def my_tamagotchis(self, info) -> List[Tamagotchi]:
        user_id = getattr(info.context.get("request", {}), "user_id", None)
        if user_id:
            return storage.get_user_tamagotchis(user_id)
        return []
    
    @strawberry.field
    def all_users(self) -> List[User]:
        return [storage.get_user(user_id) for user_id in storage.users.keys()]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def register(self, input: CreateUserInput) -> AuthPayload:
        try:
            user = storage.create_user(input.username, input.password)
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.id}, expires_delta=access_token_expires
            )
            return AuthPayload(token=access_token, user=user)
        except ValueError as e:
            raise Exception(str(e))
    
    @strawberry.mutation
    def login(self, input: LoginInput) -> AuthPayload:
        user = storage.authenticate_user(input.username, input.password)
        if not user:
            raise Exception("Invalid credentials")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
        return AuthPayload(token=access_token, user=user)
    
    @strawberry.mutation
    def create_tamagotchi(self, input: CreateTamagotchiInput, info) -> Tamagotchi:
        user_id = getattr(info.context.get("request", {}), "user_id", None)
        if not user_id:
            raise Exception("Authentication required")
        return storage.create_tamagotchi(input.name, user_id)
    
    @strawberry.mutation
    def update_mouse_position(self, input: MousePositionInput, info) -> bool:
        user_id = getattr(info.context.get("request", {}), "user_id", None)
        if not user_id:
            raise Exception("Authentication required")
        storage.update_mouse_position(user_id, input.x, input.y)
        return True

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def tamagotchi_updates(self) -> AsyncGenerator[str, None]:
        # This is a placeholder - real implementation would use WebSocket manager
        while True:
            yield "Update available"
            await asyncio.sleep(1)

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)

# FastAPI app
app = FastAPI(title="Multiplayer Tamagotchi Game API")

@app.on_event("startup")
async def startup_event():
    await storage.start_background_tasks()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL endpoint
graphql_app = GraphQLRouter(
    schema,
    subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL]
)
app.include_router(graphql_app, prefix="/graphql")

# WebSocket endpoint for real-time updates
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    connection_id = await manager.connect(websocket, user_id)
    
    # Set user as online
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
        
        # Set user as offline
        if user_id in storage.users:
            storage.users[user_id]['is_online'] = False
            storage.save_data()

# Serve static files (for Vue.js frontend)
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)