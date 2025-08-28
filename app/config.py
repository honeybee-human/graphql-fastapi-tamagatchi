from passlib.context import CryptContext
from fastapi.security import HTTPBearer


SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


GAME_AREA_WIDTH = 800
GAME_AREA_HEIGHT = 600
TAMAGOTCHI_EMOJIS = ['🐱', '🐶', '🐰', '🐸', '🐧', '🐨', '🦊', '🐼']


STATS_UPDATE_INTERVAL = 1
POSITION_UPDATE_INTERVAL = 0.1
