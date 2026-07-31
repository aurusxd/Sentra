
from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    NEEDS_SETUP = "needs_setup"

class EmployeeCreate(BaseModel):
    name: str
    role: str
    business_description: str | None = None
    language: str = "ru"
    tone: str = "friendly"
    instruction: str
    fallback_message: str
    telegram_admin_chat_id: str | None = None
    max_admin_chat_id: str | None = None


class EmployeeUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    business_description: str | None = None
    language: str | None = None
    tone: str | None = None
    instruction: str | None = None
    fallback_message: str | None = None
    telegram_admin_chat_id: str | None = None
    max_admin_chat_id: str | None = None
    status: EmployeeStatus | None = None


class EmployeeRead(BaseModel):
    id: int
    name: str
    role: str
    business_description: str | None
    language: str
    tone: str
    instruction: str
    fallback_message: str
    telegram_admin_chat_id: str | None
    max_admin_chat_id: str | None
    status: EmployeeStatus
    created_at: datetime
    updated_at: datetime | None
    telegram_connected: bool = False
    telegram_bot_username: str | None = None
    telegram_connected_at: datetime | None = None
    max_connected: bool = False
    max_bot_username: str | None = None
    max_connected_at: datetime | None = None
    dialogs_count: int = 0
    active_dialogs_count: int = 0
    human_pending_count: int = 0

    model_config = {
        "from_attributes": True
    }


