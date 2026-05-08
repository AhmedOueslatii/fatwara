import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


class InvalidToken(Exception):
    pass


def issue_token(user_id: uuid.UUID) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=settings.JWT_LIFETIME_SECONDS)).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> uuid.UUID:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.PyJWTError as exc:
        raise InvalidToken(str(exc)) from exc
    sub = payload.get("sub")
    if not sub:
        raise InvalidToken("missing sub")
    try:
        return uuid.UUID(sub)
    except ValueError as exc:
        raise InvalidToken("sub is not a uuid") from exc
