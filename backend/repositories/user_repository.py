from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.utils.depends import provider
from backend.database.models.user import User


class UserRepository:
    @provider.inject_session
    async def get_all(
        self,
        session: AsyncSession,
    ) -> list[User]:
        result = await session.execute(select(User)) 
        return list(result.scalars().all())

    @provider.inject_session
    async def get_by_id(
        self,
        user_id: int,
        session: AsyncSession,
    ) -> User | None:
        result = await session.execute(
            select(User).where(
                User.id == user_id
            )
        )
        return result.scalar_one_or_none()

    @provider.inject_session
    async def get_by_name(
        self,
        name: str,
        session: AsyncSession,
    ) -> User | None:
        result = await session.execute(
            select(User).where(
                User.name == name
            )
        )
        return result.scalar_one_or_none()

    @provider.inject_session
    async def create(
        self,
        user: User,
        session: AsyncSession,
    ) -> User:
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    @provider.inject_session
    async def update(
        self,
        user: User,
        session: AsyncSession,
    ) -> User:
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    @provider.inject_session
    async def delete(
        self,
        user: User,
        session: AsyncSession,
    ) -> User:
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user