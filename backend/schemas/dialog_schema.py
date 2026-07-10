from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.database.enums import DialogStatus, SenderType


class MessageRead(BaseModel):
    id: int
    dialog_id: int
    sender_type: SenderType
    text: str
    external_message_id: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DialogRead(BaseModel):
    id: int
    employee_id: int
    channel_id: int | None
    client_external_id: str
    client_name: str | None
    client_username: str | None
    status: DialogStatus
    is_human_takeover: bool
    created_at: datetime
    updated_at: datetime | None
    messages: list[MessageRead] = []

    model_config = ConfigDict(from_attributes=True)


class HumanMessageCreate(BaseModel):
    text: str
