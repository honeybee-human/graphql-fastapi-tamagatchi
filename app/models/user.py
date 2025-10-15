import strawberry

@strawberry.type
class User:
    id: str
    username: str
    created_at: str
    mouse_x: float = 0.0
    mouse_y: float = 0.0
    is_online: bool = False
    # Difficulty multiplier for stat deterioration (0.25x - 4x). Default 1.0
    difficulty: float = 1.0

@strawberry.type
class MousePosition:
    user_id: str
    username: str
    x: float
    y: float
    timestamp: str