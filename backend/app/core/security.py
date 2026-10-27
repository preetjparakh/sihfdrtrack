from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from pydantic import BaseModel
from backend.app.core.config import settings
from backend.app.core.clock import clock_service

class TokenPayload(BaseModel):
    sub: str
    email: str
    role: str  # COLLEGE, OFFICER, APPROVER
    institution_id: Optional[str] = None
    exp: Optional[int] = None

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now = clock_service.now_utc()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp()), "iat": int(now.timestamp())})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False},
        )
        expires_at = payload.get("exp")
        if expires_at is not None and int(expires_at) <= int(clock_service.now_utc().timestamp()):
            return None
        return TokenPayload(
            sub=payload.get("sub"),
            email=payload.get("email"),
            role=payload.get("role"),
            institution_id=payload.get("institution_id"),
            exp=payload.get("exp")
        )
    except JWTError:
        return None
