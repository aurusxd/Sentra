from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ChannelType(str, Enum):
    TELEGRAM = "telegram"


class ChannelStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class ChannelConnect(BaseModel):
    token: str
    type: ChannelType


class ChannelRead(BaseModel):
    id: int

    employee_id: int

    type: ChannelType

    external_id: str | None

    external_username: str | None

    status: ChannelStatus

    created_at: datetime
    connected_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class ChannelUpdate(BaseModel):
    status: ChannelStatus


class TelegramConnectionStatus(BaseModel):
    connected: bool

    bot_name: str | None

    bot_username: str | None

    status: ChannelStatus
