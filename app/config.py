from passlib.context import CryptContext
from fastapi.security import HTTPBearer

# Security configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
# Use pbkdf2_sha256 (pure Python via hashlib) to avoid bcrypt binary builds
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
security = HTTPBearer()

# Game configuration
GAME_AREA_WIDTH = 800
GAME_AREA_HEIGHT = 600
TAMAGOTCHI_EMOJIS = ['🐱', '🐶', '🐰', '🐸', '🐧', '🐨', '🦊', '🐼']

# Update intervals
STATS_UPDATE_INTERVAL = 1  # seconds
POSITION_UPDATE_INTERVAL = 0.1  # seconds
DEBOUNCE_DELAY_SEC = 2.0  # debounce delay for scheduled saves
BACKUP_INTERVAL_SEC = 30.0  # interval for periodic backup saves