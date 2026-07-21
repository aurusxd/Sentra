from datetime import datetime, timezone

from fastapi import HTTPException, status

from backend.database.models.channel import Channel
from backend.database.enums import ChannelStatus, ChannelType
from backend.repositories.channel_repository import ChannelRepository
from backend.schemas.channel_schema import ChannelConnect
from backend.utils.toeken_crypto import encrypt_token
from backend.utils.webhook_secret import generate_webhook_secret


class ChannelService:
    def __init__(self):
        self.repository = ChannelRepository()

    async def get_by_id(self, channel_id: int) -> Channel:
        channel = await self.repository.get_by_id(channel_id=channel_id)

        if channel is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found",
            )

        return channel

    async def get_by_employee_id(self, employee_id: int) -> list[Channel]:
        return await self.repository.get_by_employee_id(
            employee_id=employee_id,
        )

    async def get_telegram_by_employee_id(self, employee_id: int) -> Channel | None:
        return await self.repository.get_telegram_by_employee_id(
            employee_id=employee_id,
        )

    async def get_max_by_employee_id(self, employee_id: int) -> Channel | None:
        return await self.repository.get_max_by_employee_id(
            employee_id=employee_id,
        )

    async def create(
        self,
        data: ChannelConnect,
        employee_id: int,
        bot_id: int,
        bot_username: str | None,
    ) -> Channel:
        existing_channel = await self.repository.get_by_external_id(
            channel_type=data.type,
            external_id=str(bot_id),
        )

        employee_channel = (
            await self.repository.get_telegram_by_employee_id(employee_id=employee_id)
            if data.type == ChannelType.TELEGRAM
            else await self.repository.get_max_by_employee_id(employee_id=employee_id)
        )

        if existing_channel is not None and existing_channel.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This bot is already connected",
            )

        if employee_channel is not None:
            if existing_channel is not None and existing_channel.id != employee_channel.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"This employee already has another {data.type.value} channel",
                )

            employee_channel.token_encrypted = encrypt_token(data.token)
            employee_channel.external_id = str(bot_id)
            employee_channel.external_username = bot_username
            employee_channel.webhook_secret = employee_channel.webhook_secret or generate_webhook_secret()
            employee_channel.status = ChannelStatus.CONNECTED
            employee_channel.connected_at = datetime.now(timezone.utc)

            return await self.repository.update(channel=employee_channel)

        channel = Channel(
            employee_id=employee_id,
            type=data.type,
            token_encrypted=encrypt_token(data.token),
            external_id=str(bot_id),
            external_username=bot_username,
            webhook_secret=generate_webhook_secret(),
            status=ChannelStatus.CONNECTED,
            connected_at=datetime.now(timezone.utc),
        )

        return await self.repository.create(channel=channel)

    async def update(
        self,
        channel_id: int,
        data,
    ) -> Channel:
        channel = await self.get_by_id(channel_id=channel_id)

        values = data.model_dump(exclude_unset=True)

        for key, value in values.items():
            setattr(channel, key, value)

        return await self.repository.update(channel=channel)

    async def disconnect(
        self,
        employee_id: int,
        channel_type: ChannelType = ChannelType.TELEGRAM,
    ) -> Channel:
        channel = (
            await self.repository.get_telegram_by_employee_id(employee_id=employee_id)
            if channel_type == ChannelType.TELEGRAM
            else await self.repository.get_max_by_employee_id(employee_id=employee_id)
        )

        if channel is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{channel_type.value.capitalize()} channel not found",
            )

        channel.status = ChannelStatus.DISCONNECTED
        channel.connected_at = None

        return await self.repository.update(channel=channel)

    async def delete(self, channel_id: int) -> dict:
        channel = await self.get_by_id(channel_id=channel_id)

        await self.repository.delete(channel=channel)

        return {"message": "Channel deleted"}
    

    async def get_by_webhook_secret(self, webhook_secret: str):
        return await self.repository.get_by_webhook_secret(
            webhook_secret=webhook_secret,
    )
