from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database.models.dialog import Dialog
from backend.database.enums import DialogStatus
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
            select(Dialog)
            .options(
                selectinload(Dialog.channel),
                selectinload(Dialog.messages),
            )
            .where(Dialog.id == dialog_id)
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
            .options(selectinload(Dialog.messages))
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

    @provider.inject_session
    async def get_by_max_admin_notification_id(
        self,
        channel_id: int,
        notification_message_id: str,
        session: AsyncSession,
    ) -> Dialog | None:
        result = await session.execute(
            select(Dialog).where(
                Dialog.channel_id == channel_id,
                Dialog.max_admin_notification_message_id == notification_message_id,
            )
        )
        return result.scalar_one_or_none()

    @provider.inject_session
    async def get_active_max_operator_dialog(
        self,
        channel_id: int,
        admin_chat_id: str,
        session: AsyncSession,
    ) -> Dialog | None:
        result = await session.execute(
            select(Dialog).where(
                Dialog.channel_id == channel_id,
                Dialog.max_operator_chat_id == admin_chat_id,
                Dialog.is_human_takeover.is_(True),
            )
        )
        return result.scalar_one_or_none()

    @provider.inject_session
    async def clear_max_operator_sessions(
        self,
        channel_id: int,
        admin_chat_id: str,
        except_dialog_id: int | None,
        session: AsyncSession,
    ) -> None:
        conditions = [
            Dialog.channel_id == channel_id,
            Dialog.max_operator_chat_id == admin_chat_id,
        ]
        if except_dialog_id is not None:
            conditions.append(Dialog.id != except_dialog_id)

        await session.execute(
            update(Dialog)
            .where(*conditions)
            .values(
                max_operator_chat_id=None,
                max_operator_user_id=None,
                is_human_takeover=False,
                status=DialogStatus.ACTIVE,
            )
        )
