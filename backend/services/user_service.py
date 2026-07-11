from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from backend.core.password import hash_password
from backend.database.models.user import User
from backend.repositories.user_repository import UserRepository
from backend.schemas.user_schema import UserCreate


class UserService:
    def __init__(self):
        self.repository = UserRepository()

    async def get_all(self):
        return await self.repository.get_all()

    async def get_by_id(self, user_id: int) -> User:
        user = await self.repository.get_by_id(
            user_id=user_id
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user

    async def get_by_name(self, name: str) -> User | None:
        return await self.repository.get_by_name(
            name=name
        )

    async def create(self,data: UserCreate):
        values = data.model_dump()
        values["password_hash"] = hash_password(values.pop("password"))
        user = User(**values)
        try:
            return await self.repository.create(user=user)
        except IntegrityError as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username or email already exists",
            ) from error

    async def delete(self, user_id: int):
        user = await self.get_by_id(
            user_id=user_id
        )
        return await self.repository.delete(user=user)
    
user_service = UserService()
