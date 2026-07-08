import secrets


def generate_webhook_secret() -> str:
    return secrets.token_urlsafe(32)