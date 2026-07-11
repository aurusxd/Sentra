import asyncio
import os

from backend.schemas.user_schema import UserCreate
from backend.services.user_service import user_service


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


async def create_admin() -> None:
    email = required_env("REGISTRATION_ADMIN_EMAIL")
    user = await user_service.create(
        data=UserCreate(
            name=required_env("BOOTSTRAP_ADMIN_NAME"),
            email=email,
            password=required_env("BOOTSTRAP_ADMIN_PASSWORD"),
        )
    )
    print(f"Registration administrator created: id={user.id}, email={user.email}")


if __name__ == "__main__":
    asyncio.run(create_admin())
