
from enum import Enum


class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    NEEDS_SETUP = "needs_setup"


class KnowledgeFileStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class ChannelType(str, Enum):
    TELEGRAM = "telegram"
    MAX = "max"


class ChannelStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class DialogStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    NEEDS_HUMAN = "needs_human"


class SenderType(str, Enum):
    CLIENT = "client"
    EMPLOYEE = "employee"
    HUMAN = "human"


class TelegramConnection(str, Enum):
    CONNECTED="connected"
    DISCONNECTED="disconnected"
