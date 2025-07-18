from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import strawberry
from strawberry.fastapi import GraphQLRouter
from datetime import datetime, timedelta
import asyncio
from typing import Optional, List
import json
import os

# Tamagotchi data model
@strawberry.type
class Tamagotchi:
    id: str
    name: str
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

# Input types
@strawberry.input
class CreateTamagotchiInput:
    name: str

@strawberry.input
class ActionInput:
    tamagotchi_id: str

# Simple in-memory storage (in production, use a real database)
class TamagotchiStorage:
    def __init__(self):
        self.tamagotchis = {}
        self.load_data()
    
    def save_data(self):
        with open('tamagotchis.json', 'w') as f:
            json.dump(self.tamagotchis, f, indent=2)
    
    def load_data(self):
        if os.path.exists('tamagotchis.json'):
            with open('tamagotchis.json', 'r') as f:
                self.tamagotchis = json.load(f)
    
    def create_tamagotchi(self, name: str) -> Tamagotchi:
        import uuid
        tamagotchi_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        tamagotchi_data = {
            'id': tamagotchi_id,
            'name': name,
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
            'status': 'Happy'
        }
        
        self.tamagotchis[tamagotchi_id] = tamagotchi_data
        self.save_data()
        return Tamagotchi(**tamagotchi_data)
    
    def get_tamagotchi(self, tamagotchi_id: str) -> Optional[Tamagotchi]:
        data = self.tamagotchis.get(tamagotchi_id)
        if data:
            self.update_stats(tamagotchi_id)
            return Tamagotchi(**self.tamagotchis[tamagotchi_id])
        return None
    
    def get_all_tamagotchis(self) -> List[Tamagotchi]:
        result = []
        for tamagotchi_id in self.tamagotchis:
            self.update_stats(tamagotchi_id)
            result.append(Tamagotchi(**self.tamagotchis[tamagotchi_id]))
        return result
    
    def update_stats(self, tamagotchi_id: str):
        if tamagotchi_id not in self.tamagotchis:
            return
        
        tamagotchi = self.tamagotchis[tamagotchi_id]
        now = datetime.now()
        
        # Calculate time differences
        last_fed = datetime.fromisoformat(tamagotchi['last_fed'])
        last_played = datetime.fromisoformat(tamagotchi['last_played'])
        last_slept = datetime.fromisoformat(tamagotchi['last_slept'])
        
        # Update stats based on time passed
        hours_since_fed = (now - last_fed).total_seconds() / 3600
        hours_since_played = (now - last_played).total_seconds() / 3600
        hours_since_slept = (now - last_slept).total_seconds() / 3600
        
        # Increase hunger over time
        tamagotchi['hunger'] = min(100, tamagotchi['hunger'] + int(hours_since_fed * 10))
        
        # Decrease happiness over time
        tamagotchi['happiness'] = max(0, tamagotchi['happiness'] - int(hours_since_played * 5))
        
        # Decrease energy over time
        tamagotchi['energy'] = max(0, tamagotchi['energy'] - int(hours_since_slept * 8))
        
        # Update health based on other stats
        if tamagotchi['hunger'] > 80 or tamagotchi['happiness'] < 20 or tamagotchi['energy'] < 20:
            tamagotchi['health'] = max(0, tamagotchi['health'] - 1)
        
        # Update status
        if tamagotchi['health'] <= 0:
            tamagotchi['is_alive'] = False
            tamagotchi['status'] = 'Dead'
        elif tamagotchi['hunger'] > 80:
            tamagotchi['status'] = 'Starving'
        elif tamagotchi['energy'] < 20:
            tamagotchi['status'] = 'Tired'
        elif tamagotchi['happiness'] < 30:
            tamagotchi['status'] = 'Sad'
        else:
            tamagotchi['status'] = 'Happy'
        
        # Age the tamagotchi
        created_at = datetime.fromisoformat(tamagotchi['created_at'])
        tamagotchi['age'] = int((now - created_at).total_seconds() / 3600)  # Age in hours
        
        self.save_data()
    
    def feed_tamagotchi(self, tamagotchi_id: str) -> Optional[Tamagotchi]:
        if tamagotchi_id not in self.tamagotchis:
            return None
        
        tamagotchi = self.tamagotchis[tamagotchi_id]
        if not tamagotchi['is_alive']:
            return Tamagotchi(**tamagotchi)
        
        tamagotchi['hunger'] = max(0, tamagotchi['hunger'] - 30)
        tamagotchi['happiness'] = min(100, tamagotchi['happiness'] + 10)
        tamagotchi['last_fed'] = datetime.now().isoformat()
        
        self.save_data()
        self.update_stats(tamagotchi_id)
        return Tamagotchi(**self.tamagotchis[tamagotchi_id])
    
    def play_with_tamagotchi(self, tamagotchi_id: str) -> Optional[Tamagotchi]:
        if tamagotchi_id not in self.tamagotchis:
            return None
        
        tamagotchi = self.tamagotchis[tamagotchi_id]
        if not tamagotchi['is_alive']:
            return Tamagotchi(**tamagotchi)
        
        tamagotchi['happiness'] = min(100, tamagotchi['happiness'] + 20)
        tamagotchi['energy'] = max(0, tamagotchi['energy'] - 10)
        tamagotchi['last_played'] = datetime.now().isoformat()
        
        self.save_data()
        self.update_stats(tamagotchi_id)
        return Tamagotchi(**self.tamagotchis[tamagotchi_id])
    
    def sleep_tamagotchi(self, tamagotchi_id: str) -> Optional[Tamagotchi]:
        if tamagotchi_id not in self.tamagotchis:
            return None
        
        tamagotchi = self.tamagotchis[tamagotchi_id]
        if not tamagotchi['is_alive']:
            return Tamagotchi(**tamagotchi)
        
        tamagotchi['energy'] = min(100, tamagotchi['energy'] + 40)
        tamagotchi['last_slept'] = datetime.now().isoformat()
        
        self.save_data()
        self.update_stats(tamagotchi_id)
        return Tamagotchi(**self.tamagotchis[tamagotchi_id])

# Initialize storage
storage = TamagotchiStorage()

# GraphQL Schema
@strawberry.type
class Query:
    @strawberry.field
    def tamagotchi(self, id: str) -> Optional[Tamagotchi]:
        return storage.get_tamagotchi(id)
    
    @strawberry.field
    def all_tamagotchis(self) -> List[Tamagotchi]:
        return storage.get_all_tamagotchis()

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_tamagotchi(self, input: CreateTamagotchiInput) -> Tamagotchi:
        return storage.create_tamagotchi(input.name)
    
    @strawberry.mutation
    def feed_tamagotchi(self, input: ActionInput) -> Optional[Tamagotchi]:
        return storage.feed_tamagotchi(input.tamagotchi_id)
    
    @strawberry.mutation
    def play_with_tamagotchi(self, input: ActionInput) -> Optional[Tamagotchi]:
        return storage.play_with_tamagotchi(input.tamagotchi_id)
    
    @strawberry.mutation
    def sleep_tamagotchi(self, input: ActionInput) -> Optional[Tamagotchi]:
        return storage.sleep_tamagotchi(input.tamagotchi_id)

schema = strawberry.Schema(query=Query, mutation=Mutation)

# FastAPI app
app = FastAPI(title="Tamagotchi Game API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL endpoint
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# Serve static files (for Vue.js frontend)
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)