from .user import User
from .tamagotchi import Tamagotchi, Position, PositionUpdate, TamagotchiUpdateType
from .inputs import (
    CreateUserInput,
    LoginInput,
    CreateTamagotchiInput,
    ActionInput,
    MousePositionInput,
    AuthPayload
)

__all__ = [
    "User",
    "Tamagotchi",
    "Position",
    "PositionUpdate",
    "TamagotchiUpdateType",
    "CreateUserInput",
    "LoginInput",
    "CreateTamagotchiInput",
    "ActionInput",
    "MousePositionInput",
    "AuthPayload"
]
