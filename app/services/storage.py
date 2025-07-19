import asyncio
import json
import math
import os
import random
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from ..config import pwd_context, TAMAGOTCHI_EMOJIS, GAME_AREA_WIDTH, GAME_AREA_HEIGHT
from ..models import User, Tamagotchi, Position

class GameStorage:
    def __init__(self):
        self.users: Dict[str, dict] = {}
        self.tamagotchis: Dict[str, dict] = {}
        self.mouse_positions: Dict[str, dict] = {}
        self.load_data()
        self._tasks_started = False
        self.manager = None  # Will be set by dependency injection
    
    def set_connection_manager(self, manager):
        """Set the connection manager for broadcasting"""
        self.manager = manager
    
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
        x = random.uniform(50, GAME_AREA_WIDTH - 50)
        y = random.uniform(50, GAME_AREA_HEIGHT - 50)
        direction = random.uniform(0, 2 * math.pi)
        
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
            'emoji': random.choice(TAMAGOTCHI_EMOJIS)
        }
        
        self.tamagotchis[tamagotchi_id] = tamagotchi_data
        self.save_data()
        
        # Broadcast new tamagotchi
        if self.manager:
            asyncio.create_task(self.manager.broadcast({
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
            if self.manager:
                asyncio.create_task(self.manager.broadcast({
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
                if self.manager:
                    await self.manager.broadcast({
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
                if pos['x'] <= 0 or pos['x'] >= GAME_AREA_WIDTH:
                    pos['direction'] = math.pi - pos['direction']
                    pos['x'] = max(0, min(GAME_AREA_WIDTH, pos['x']))
                
                if pos['y'] <= 0 or pos['y'] >= GAME_AREA_HEIGHT:
                    pos['direction'] = -pos['direction']
                    pos['y'] = max(0, min(GAME_AREA_HEIGHT, pos['y']))
                
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
                if self.manager:
                    await self.manager.broadcast({
                        'type': 'position_update',
                        'positions': updated_positions
                    })