from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.domain.core.settings import get_settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(
    subject,
    expires_delta=timedelta(minutes=get_settings().access_token_expire_minute),
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": subject, "exp": expire, "type": "bearer"}
    return jwt.encode(payload, key=get_settings().secret_key, algorithm=get_settings().algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, get_settings().secret_key, algorithms=[get_settings().algorithm])
