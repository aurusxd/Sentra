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
    

dialog_service = DialogService()