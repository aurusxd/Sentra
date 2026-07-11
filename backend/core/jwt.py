from datetime import datetime, timedelta, timezone

import jwt

from backend.config import JWT_KEY

ALGORITHM = "HS256"


def get_jwt_key() -> str:
    if not JWT_KEY or len(JWT_KEY) < 32:
        raise RuntimeError("JWT_KEY must contain at least 32 characters")
    return JWT_KEY


def create_access_token(
    user_id: int,
    expires_minutes: int = 60 * 24,
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        get_jwt_key(),
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token,
            get_jwt_key(),
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            return None

        return int(user_id)

    except (jwt.InvalidTokenError, ValueError):
        return None
