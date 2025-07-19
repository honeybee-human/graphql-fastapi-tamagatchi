import strawberry
from .user import User

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