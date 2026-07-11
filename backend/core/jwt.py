from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from backend.config import JWT_KEY, config

ALGORITHM = "HS256"


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
        JWT_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token,
            JWT_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            return None

        return int(user_id)

    except JWTError:
        return None