import strawberry
import asyncio
import json
from typing import AsyncGenerator, Dict, Any, List, Optional

from ..models.tamagotchi import TamagotchiUpdateType, Tamagotchi, PositionUpdate
from ..services.websocket import ConnectionManager
from ..services.storage import GameStorage

manager: ConnectionManager = None
storage: GameStorage = None

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def tamagotchi_updates(self) -> AsyncGenerator[TamagotchiUpdateType, None]:
        # Create a queue to receive updates
        queue = asyncio.Queue()
        
        # Register this subscription with the connection manager
        subscription_id = id(queue)
        
        # Custom message handler that puts messages in our queue
        async def message_handler(message: Dict[str, Any]):
            message_type = message.get('type')
            
            if message_type == 'stats_update':
                # Convert the tamagotchis data to proper objects
                tamagotchis_data = message.get('tamagotchis', [])
                if tamagotchis_data and len(tamagotchis_data) > 0:
                    # For simplicity, we'll just use the first tamagotchi in the update
                    tamagotchi_data = tamagotchis_data[0]
                    tamagotchi = await storage.get_tamagotchi_by_id(tamagotchi_data['id'])
                    await queue.put(TamagotchiUpdateType(
                        type=message_type,
                        tamagotchi=tamagotchi
                    ))
            
            elif message_type == 'position_update':
                positions_data = message.get('positions', [])
                if positions_data:
                    positions = [PositionUpdate(
                        id=pos['id'],
                        x=pos['x'],
                        y=pos['y'],
                        direction=pos['direction']
                    ) for pos in positions_data]
                    
                    await queue.put(TamagotchiUpdateType(
                        type=message_type,
                        positions=positions
                    ))
            
            elif message_type == 'tamagotchi_created':
                tamagotchi_data = message.get('tamagotchi')
                if tamagotchi_data:
                    tamagotchi = await storage.get_tamagotchi_by_id(tamagotchi_data['id'])
                    await queue.put(TamagotchiUpdateType(
                        type=message_type,
                        tamagotchi=tamagotchi
                    ))
        
        # Register the handler with the connection manager
        if manager:
            manager.register_subscription_handler(subscription_id, message_handler)
        
        try:
            while True:
                # Wait for messages to be put in the queue
                update = await queue.get()
                yield update
        finally:
            # Clean up when the subscription ends
            if manager:
                manager.unregister_subscription_handler(subscription_id)
