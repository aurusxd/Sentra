from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.dialog import Dialog
from backend.utils.depends import provider


class DialogRepository:
    @provider.inject_session
    async def create(
        self,
        dialog: Dialog,
        session: AsyncSession,
    ) -> Dialog:
        session.add(dialog)
        await session.flush()
        await session.refresh(dialog)

        return dialog

    @provider.inject_session
    async def update(
        self,
        dialog: Dialog,
        session: AsyncSession,
    ) -> Dialog:
        session.add(dialog)
        await session.flush()
        await session.refresh(dialog)

        return dialog

    @provider.inject_session
    async def get_by_id(
        self,
        dialog_id: int,
        session: AsyncSession,
    ) -> Dialog | None:
        result = await session.execute(
            select(Dialog).where(Dialog.id == dialog_id)
        )

        return result.scalar_one_or_none()

    @provider.inject_session
    async def get_by_employee_id(
        self,
        employee_id: int,
        session: AsyncSession,
    ) -> list[Dialog]:
        result = await session.execute(
            select(Dialog)
            .where(Dialog.employee_id == employee_id)
            .order_by(Dialog.updated_at.desc())
        )

        return list(result.scalars().all())

    @provider.inject_session
    async def get_by_external_chat_id(
        self,
        channel_id: int,
        client_external_id: str,
        session: AsyncSession,
    ) -> Dialog | None:
        result = await session.execute(
            select(Dialog).where(
                Dialog.channel_id == channel_id,
                Dialog.client_external_id == client_external_id,
            )
        )

        return result.scalar_one_or_none()