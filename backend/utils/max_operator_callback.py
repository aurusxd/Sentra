import hashlib
import hmac

from backend.core.jwt import get_jwt_key

ALLOWED_ACTIONS = {"take", "close"}


def create_max_operator_callback(action: str, dialog_id: int) -> str:
    if action not in ALLOWED_ACTIONS:
        raise ValueError("Unsupported MAX operator action")
    value = f"operator:{action}:{dialog_id}"
    signature = hmac.new(
        get_jwt_key().encode(),
        value.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{value}:{signature}"


def parse_max_operator_callback(payload: str) -> tuple[str, int] | None:
    parts = payload.split(":")
    if len(parts) != 4 or parts[0] != "operator" or parts[1] not in ALLOWED_ACTIONS:
        return None
    try:
        dialog_id = int(parts[2])
    except ValueError:
        return None

    value = ":".join(parts[:3])
    expected_signature = hmac.new(
        get_jwt_key().encode(),
        value.encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(parts[3], expected_signature):
        return None
    return parts[1], dialog_id
