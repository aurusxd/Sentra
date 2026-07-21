from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.enums import SenderType
from backend.database.models.message import Message
from backend.utils.depends import provider


class MessageRepository:
    @provider.inject_session
    async def create(
        self,
        message: Message,
        session: AsyncSession,
    ) -> Message:
        session.add(message)
        await session.flush()
        await session.refresh(message)

        return message

    @provider.inject_session
    async def get_by_dialog_id(
        self,
        dialog_id: int,
        session: AsyncSession,
    ) -> list[Message]:
        result = await session.execute(
            select(Message)
            .where(Message.dialog_id == dialog_id)
            .order_by(Message.created_at.asc(), Message.id.asc())
        )

        return list(result.scalars().all())

    @provider.inject_session
    async def client_message_exists(
        self,
        dialog_id: int,
        external_message_id: str,
        session: AsyncSession,
    ) -> bool:
        result = await session.execute(
            select(Message.id).where(
                Message.dialog_id == dialog_id,
                Message.sender_type == SenderType.CLIENT,
                Message.external_message_id == external_message_id,
            )
        )
        return result.scalar_one_or_none() is not None

    @provider.inject_session
    async def get_last_by_dialog_id(
        self,
        dialog_id: int,
        limit: int,
        session: AsyncSession,
    ) -> list[Message]:
        result = await session.execute(
            select(Message)
            .where(Message.dialog_id == dialog_id)
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(limit)
        )

        messages = list(result.scalars().all())

        return list(reversed(messages))

    @provider.inject_session
    async def delete_by_dialog_id(
        self,
        dialog_id: int,
        session: AsyncSession,
    ) -> None:
        messages = await self.get_by_dialog_id(
            dialog_id=dialog_id,
            session=session,
        )

        for message in messages:
            await session.delete(message)

        await session.flush()
