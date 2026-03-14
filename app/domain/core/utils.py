from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.domain.core.settings import get_settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(subject) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=get_settings().access_token_expire_minute
    )
    payload = {"sub": subject, "exp": expire, "type": "bearer"}
    return jwt.encode(payload, key=get_settings().secret_key, algorithm=get_settings().algorithm)
