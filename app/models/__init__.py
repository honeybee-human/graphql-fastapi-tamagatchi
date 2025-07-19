from .user import User
from .tamagotchi import Tamagotchi, Position
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
    "CreateUserInput",
    "LoginInput",
    "CreateTamagotchiInput",
    "ActionInput",
    "MousePositionInput",
    "AuthPayload"
]