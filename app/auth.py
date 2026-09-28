from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from werkzeug.security import check_password_hash, generate_password_hash
from .config import settings

ALGORITHM = "HS256"
COOKIE_NAME = "pocketsmart_token"

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)

def create_access_token(user_id: int) -> str:
    payload = {"sub": str(user_id), "exp": datetime.now(timezone.utc) + timedelta(hours=12)}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)

def get_user_id_from_token(token: str | None) -> int | None:
    if not token: return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (JWTError, KeyError, TypeError, ValueError):
        return None
