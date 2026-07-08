from cryptography.fernet import Fernet

from backend.config import TOKEN_ENCRYPTION_KEY

tokens="04kGMbLKKZl2cIJ8l34vWfdYOgsBBR197a0JOP4Ylbg="
fernet = Fernet(tokens.encode())


def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    return fernet.decrypt(encrypted_token.encode()).decode()