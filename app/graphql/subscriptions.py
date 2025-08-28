import strawberry
import asyncio
from typing import AsyncGenerator

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def tamagotchi_updates(self) -> AsyncGenerator[str, None]:

        while True:
            yield "Update available"
            await asyncio.sleep(1)
