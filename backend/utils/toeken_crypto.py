from cryptography.fernet import Fernet

from backend.config import TOKEN_ENCRYPTION_KEY

def get_fernet() -> Fernet:
    if not TOKEN_ENCRYPTION_KEY:
        raise RuntimeError("TOKEN_ENCRYPTION_KEY is not configured")
    return Fernet(TOKEN_ENCRYPTION_KEY.encode())


def encrypt_token(token: str) -> str:
    return get_fernet().encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    return get_fernet().decrypt(encrypted_token.encode()).decode()
