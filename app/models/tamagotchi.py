import strawberry

@strawberry.type
class Position:
    x: float
    y: float
    direction: float  # angle in radians
    speed: float = 1.0

@strawberry.type
class Tamagotchi:
    id: str
    name: str
    owner_id: str
    happiness: int
    hunger: int
    energy: int
    health: int
    age: int
    last_fed: str
    last_played: str
    last_slept: str
    created_at: str
    is_alive: bool
    status: str
    position: Position
    emoji: str