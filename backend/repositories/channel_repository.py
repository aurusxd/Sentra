from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.channel import Channel
from backend.utils.depends import provider


class ChannelRepository:
    @provider.inject_session
    async def create(
        self,
        channel: Channel,
        session: AsyncSession,
    ) -> Channel:
        session.add(channel)
        await session.flush()
        await session.refresh(channel)

        return channel

    @provider.inject_session
    async def update(
        self,
        channel: Channel,
        session: AsyncSession,
    ) -> Channel:
        session.add(channel)
        await session.flush()
        await session.refresh(channel)

        return channel

    @provider.inject_session
    async def get_by_id(
        self,
        channel_id: int,
        session: AsyncSession,
    ) -> Channel | None:
        result = await session.execute(
            select(Channel).where(Channel.id == channel_id)
        )

        return result.scalar_one_or_none()

    @provider.inject_session
    async def get_by_employee_id(
        self,
        employee_id: int,
        session: AsyncSession,
    ) -> list[Channel]:
        result = await session.execute(
            select(Channel).where(Channel.employee_id == employee_id)
        )

        return list(result.scalars().all())

    @provider.inject_session
    async def get_telegram_by_employee_id(
        self,
        employee_id: int,
        session: AsyncSession,
    ) -> Channel | None:
        result = await session.execute(
            select(Channel).where(
                Channel.employee_id == employee_id,
                Channel.type == "telegram",
            )
        )

        return result.scalar_one_or_none()


    @provider.inject_session
    async def get_max_by_employee_id(
        self,
        employee_id: int,
        session: AsyncSession,
    ) -> Channel | None:
        result = await session.execute(
            select(Channel).where(
                Channel.employee_id == employee_id,
                Channel.type == "max",
            )
        )

        return result.scalar_one_or_none()
    @provider.inject_session
    async def get_by_external_id(
        self,
        channel_type: str,
        external_id: str,
        session: AsyncSession,
    ) -> Channel | None:
        result = await session.execute(
            select(Channel).where(
                Channel.type == channel_type,
                Channel.external_id == external_id,
            )
        )

        return result.scalar_one_or_none()

    @provider.inject_session
    async def get_by_webhook_secret(
        self,
        webhook_secret: str,
        session: AsyncSession,
    ) -> Channel | None:
        result = await session.execute(
            select(Channel).where(
                Channel.webhook_secret == webhook_secret,
            )
        )

        return result.scalar_one_or_none()

    @provider.inject_session
    async def delete(
        self,
        channel: Channel,
        session: AsyncSession,
    ) -> None:
        await session.delete(channel)
        await session.flush()