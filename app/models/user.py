import strawberry

@strawberry.type
class User:
    id: str
    username: str
    created_at: str
    mouse_x: float = 0.0
    mouse_y: float = 0.0
    is_online: bool = False

@strawberry.type
class MousePosition:
    user_id: str
    username: str
    x: float
    y: float
    timestamp: str