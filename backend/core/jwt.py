from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from backend.config import config

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
        "2f3d4c0b7d8e6a9f1c2b5e8d7f9a3c1e4b6d8f0a9c2e1b7d3f5a6c8e9d0f1b2",
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token,
            "2f3d4c0b7d8e6a9f1c2b5e8d7f9a3c1e4b6d8f0a9c2e1b7d3f5a6c8e9d0f1b2",
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            return None

        return int(user_id)

    except JWTError:
        return None