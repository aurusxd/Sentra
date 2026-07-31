from fastapi import HTTPException, status

from backend.database.enums import DialogStatus
from backend.database.models.dialog import Dialog
from backend.repositories.dialog_repository import DialogRepository


class DialogService:
    def __init__(self):
        self.repository = DialogRepository()

    async def get_by_id(self, dialog_id: int) -> Dialog:
        dialog = await self.repository.get_by_id(dialog_id=dialog_id)

        if dialog is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dialog not found",
            )

        return dialog

    async def get_by_employee_id(self, employee_id: int) -> list[Dialog]:
        dialogs = await self.repository.get_by_employee_id(
            employee_id=employee_id,
        )
        if dialogs is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dialogs not found",
            )
        return dialogs
    async def get_or_create(
        self,
        employee_id: int,
        channel_id: int,
        client_external_id: str,
        client_name: str | None = None,
        client_username: str | None = None,
    ) -> Dialog:
        dialog = await self.repository.get_by_external_chat_id(
            channel_id=channel_id,
            client_external_id=client_external_id,
        )

        if dialog is not None:
            return dialog

        dialog = Dialog(
            employee_id=employee_id,
            channel_id=channel_id,
            client_external_id=client_external_id,
            client_name=client_name,
            client_username=client_username,
            status=DialogStatus.ACTIVE,
            is_human_takeover=False,
        )

        return await self.repository.create(dialog=dialog)

    async def mark_needs_human(self, dialog_id: int) -> Dialog:
        dialog = await self.get_by_id(dialog_id=dialog_id)

        dialog.status = DialogStatus.NEEDS_HUMAN

        return await self.repository.update(dialog=dialog)

    async def takeover(self, dialog_id: int) -> Dialog:
        dialog = await self.get_by_id(dialog_id=dialog_id)

        dialog.is_human_takeover = True
        dialog.status = DialogStatus.NEEDS_HUMAN

        return await self.repository.update(dialog=dialog)

    async def return_to_employee(self, dialog_id: int) -> Dialog:
        dialog = await self.get_by_id(dialog_id=dialog_id)

        dialog.is_human_takeover = False
        dialog.status = DialogStatus.ACTIVE

        return await self.repository.update(dialog=dialog)

    async def resolve(self, dialog_id: int) -> Dialog:
        dialog = await self.get_by_id(dialog_id=dialog_id)

        dialog.status = DialogStatus.RESOLVED

        return await self.repository.update(dialog=dialog)

    async def save_max_admin_notification(
        self,
        dialog_id: int,
        message_id: str,
    ) -> Dialog:
        dialog = await self.get_by_id(dialog_id=dialog_id)
        dialog.max_admin_notification_message_id = message_id
        return await self.repository.update(dialog=dialog)

    async def get_by_max_admin_notification(
        self,
        channel_id: int,
        message_id: str,
    ) -> Dialog | None:
        return await self.repository.get_by_max_admin_notification_id(
            channel_id=channel_id,
            notification_message_id=message_id,
        )

    async def get_active_max_operator_dialog(
        self,
        channel_id: int,
        admin_chat_id: str,
    ) -> Dialog | None:
        return await self.repository.get_active_max_operator_dialog(
            channel_id=channel_id,
            admin_chat_id=admin_chat_id,
        )

    async def get_single_pending_max_operator_dialog(
        self,
        channel_id: int,
    ) -> Dialog | None:
        dialogs = await self.repository.get_pending_max_operator_dialogs(
            channel_id=channel_id,
            limit=2,
        )
        return dialogs[0] if len(dialogs) == 1 else None

    async def start_max_operator_session(
        self,
        dialog_id: int,
        channel_id: int,
        admin_chat_id: str,
        admin_user_id: str,
    ) -> Dialog:
        await self.repository.clear_max_operator_sessions(
            channel_id=channel_id,
            admin_chat_id=admin_chat_id,
            except_dialog_id=dialog_id,
        )
        dialog = await self.get_by_id(dialog_id=dialog_id)
        dialog.max_operator_chat_id = admin_chat_id
        dialog.max_operator_user_id = admin_user_id
        dialog.is_human_takeover = True
        dialog.status = DialogStatus.NEEDS_HUMAN
        return await self.repository.update(dialog=dialog)

    async def stop_max_operator_session(
        self,
        dialog_id: int,
        *,
        resolved: bool = False,
    ) -> Dialog:
        dialog = await self.get_by_id(dialog_id=dialog_id)
        dialog.max_operator_chat_id = None
        dialog.max_operator_user_id = None
        dialog.is_human_takeover = False
        dialog.status = DialogStatus.RESOLVED if resolved else DialogStatus.ACTIVE
        return await self.repository.update(dialog=dialog)
    

dialog_service = DialogService()
