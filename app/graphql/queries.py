import strawberry
from typing import List, Optional

from ..models import User, Tamagotchi
from ..services.storage import GameStorage


storage: GameStorage = None

@strawberry.type
class Query:
    @strawberry.field
    def me(self, info) -> Optional[User]:

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
