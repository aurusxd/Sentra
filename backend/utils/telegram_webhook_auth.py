import hashlib
import hmac

from backend.core.jwt import get_jwt_key


def telegram_webhook_header_secret(webhook_secret: str) -> str:
    return hmac.new(
        get_jwt_key().encode(),
        webhook_secret.encode(),
        hashlib.sha256,
    ).hexdigest()
