from backend.database.enums import SenderType
from backend.database.models.message import Message
from backend.repositories.message_repository import MessageRepository


class MessageService:
    def __init__(self):
        self.repository = MessageRepository()

    async def create_client_message(
        self,
        dialog_id: int,
        text: str,
        external_message_id: str | None = None,
    ) -> Message:
        message = Message(
            dialog_id=dialog_id,
            sender_type=SenderType.CLIENT,
            text=text,
            external_message_id=external_message_id,
        )

        return await self.repository.create(message=message)

    async def client_message_exists(self, dialog_id: int, external_message_id: str) -> bool:
        return await self.repository.client_message_exists(
            dialog_id=dialog_id,
            external_message_id=external_message_id,
        )

    async def human_message_exists(self, dialog_id: int, external_message_id: str) -> bool:
        return await self.repository.message_exists(
            dialog_id=dialog_id,
            sender_type=SenderType.HUMAN,
            external_message_id=external_message_id,
        )

    async def create_employee_message(
        self,
        dialog_id: int,
        text: str,
        external_message_id: str | None = None,
    ) -> Message:
        message = Message(
            dialog_id=dialog_id,
            sender_type=SenderType.EMPLOYEE,
            text=text,
            external_message_id=external_message_id,
        )

        return await self.repository.create(message=message)

    async def create_human_message(
        self,
        dialog_id: int,
        text: str,
        external_message_id: str | None = None,
    ) -> Message:
        message = Message(
            dialog_id=dialog_id,
            sender_type=SenderType.HUMAN,
            text=text,
            external_message_id=external_message_id,
        )

        return await self.repository.create(message=message)

    async def get_dialog_messages(
        self,
        dialog_id: int,
    ) -> list[Message]:
        return await self.repository.get_by_dialog_id(
            dialog_id=dialog_id,
        )

    async def get_last_messages(
        self,
        dialog_id: int,
        limit: int = 10,
    ) -> list[Message]:
        return await self.repository.get_last_by_dialog_id(
            dialog_id=dialog_id,
            limit=limit,
        )
    
message_service = MessageService()
