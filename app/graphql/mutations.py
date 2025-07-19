import strawberry
from datetime import timedelta

from ..config import ACCESS_TOKEN_EXPIRE_MINUTES
from ..models import (
    CreateUserInput,
    LoginInput,
    CreateTamagotchiInput,
    MousePositionInput,
    AuthPayload,
    Tamagotchi
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