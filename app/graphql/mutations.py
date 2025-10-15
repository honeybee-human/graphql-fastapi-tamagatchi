import strawberry
from datetime import timedelta

from ..config import ACCESS_TOKEN_EXPIRE_MINUTES
from ..models import (
    CreateUserInput,
    LoginInput,
    CreateTamagotchiInput,
    MousePositionInput,
    AuthPayload,
    Tamagotchi,
    User,
)
from ..services.auth import create_access_token
from ..services.storage import GameStorage

# This will be injected
storage: GameStorage = None

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
        # Get user_id from context
        user_id = info.context.get("user_id")
        if not user_id:
            raise Exception("Authentication required")
        return storage.create_tamagotchi(input.name, user_id)
    
    @strawberry.mutation
    def update_mouse_position(self, input: MousePositionInput, info) -> bool:
        # Get user_id from context
        user_id = info.context.get("user_id")
        if not user_id:
            raise Exception("Authentication required")
        storage.update_mouse_position(user_id, input.x, input.y)
        return True

    @strawberry.mutation
    def update_tamagotchi_location(self, id: str, x: float, y: float, info) -> Tamagotchi:
        # Require authentication
        user_id = info.context.get("user_id")
        if not user_id:
            raise Exception("Authentication required")

        # Ensure tamagotchi exists
        t_data = storage.tamagotchis.get(id)
        if not t_data:
            raise Exception("Tamagotchi not found")

        # Enforce ownership
        if t_data.get('owner_id') != user_id:
            raise Exception("Not authorized to update this Tamagotchi")

        updated = storage.update_tamagotchi_location(id, x, y)
        if not updated:
            raise Exception("Failed to update location")
        return updated

    @strawberry.mutation
    def support_tamagotchi(self, id: str, info) -> Tamagotchi:
        # Require authentication
        user_id = info.context.get("user_id")
        if not user_id:
            raise Exception("Authentication required")

        # Ensure tamagotchi exists
        t_data = storage.tamagotchis.get(id)
        if not t_data:
            raise Exception("Tamagotchi not found")

        # Only non-owner can support
        if t_data.get('owner_id') == user_id:
            raise Exception("You cannot support your own Tamagotchi")

        updated = storage.support_tamagotchi(user_id, id)
        if not updated:
            raise Exception("Failed to support Tamagotchi")
        return updated

    @strawberry.mutation
    def feed_tamagotchi(self, id: str, info) -> Tamagotchi:
        # Require authentication
        user_id = info.context.get("user_id")
        if not user_id:
            raise Exception("Authentication required")

        # Ensure tamagotchi exists
        t_data = storage.tamagotchis.get(id)
        if not t_data:
            raise Exception("Tamagotchi not found")

        # Enforce ownership
        if t_data.get('owner_id') != user_id:
            raise Exception("Not authorized to feed this Tamagotchi")

        updated = storage.feed_tamagotchi(user_id, id)
        if not updated:
            raise Exception("Failed to feed Tamagotchi")
        return updated

    @strawberry.mutation
    def play_tamagotchi(self, id: str, info) -> Tamagotchi:
        # Require authentication
        user_id = info.context.get("user_id")
        if not user_id:
            raise Exception("Authentication required")

        # Ensure tamagotchi exists
        t_data = storage.tamagotchis.get(id)
        if not t_data:
            raise Exception("Tamagotchi not found")

        # Enforce ownership
        if t_data.get('owner_id') != user_id:
            raise Exception("Not authorized to play with this Tamagotchi")

        updated = storage.play_tamagotchi(user_id, id)
        if not updated:
            raise Exception("Failed to play with Tamagotchi")
        return updated

    @strawberry.mutation
    def sleep_tamagotchi(self, id: str, info) -> Tamagotchi:
        # Require authentication
        user_id = info.context.get("user_id")
        if not user_id:
            raise Exception("Authentication required")

        # Ensure tamagotchi exists
        t_data = storage.tamagotchis.get(id)
        if not t_data:
            raise Exception("Tamagotchi not found")

        # Enforce ownership
        if t_data.get('owner_id') != user_id:
            raise Exception("Not authorized to let this Tamagotchi sleep")

        updated = storage.sleep_tamagotchi(user_id, id)
        if not updated:
            raise Exception("Failed to update Tamagotchi sleep")
        return updated

    @strawberry.mutation
    def revive_tamagotchi(self, id: str, info) -> Tamagotchi:
        # Require authentication
        user_id = info.context.get("user_id")
        if not user_id:
            raise Exception("Authentication required")

        # Ensure tamagotchi exists
        t_data = storage.tamagotchis.get(id)
        if not t_data:
            raise Exception("Tamagotchi not found")

        # Enforce ownership
        if t_data.get('owner_id') != user_id:
            raise Exception("Not authorized to revive this Tamagotchi")

        revived = storage.revive_tamagotchi(user_id, id)
        if not revived:
            raise Exception("Failed to revive Tamagotchi")
        return revived

    @strawberry.mutation
    def release_tamagotchi(self, id: str, info) -> bool:
        # Require authentication
        user_id = info.context.get("user_id")
        if not user_id:
            raise Exception("Authentication required")

        # Ensure tamagotchi exists
        t_data = storage.tamagotchis.get(id)
        if not t_data:
            # If already gone, consider success to keep UI in sync
            return True

        # Enforce ownership
        if t_data.get('owner_id') != user_id:
            raise Exception("Not authorized to release this Tamagotchi")

        ok = storage.release_tamagotchi(user_id, id)
        if not ok:
            raise Exception("Failed to release Tamagotchi")
        return True

    @strawberry.mutation
    def set_difficulty(self, difficulty: float, info) -> User:
        # Require authentication
        user_id = info.context.get("user_id")
        if not user_id:
            raise Exception("Authentication required")
        updated_user = storage.set_user_difficulty(user_id, difficulty)
        if not updated_user:
            raise Exception("Failed to set difficulty")
        return updated_user