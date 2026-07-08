from pydantic import BaseModel

from backend.database.enums import TelegramConnection



class TelegramBotConnect(BaseModel):
    token: str

class TelegramBotCheck(BaseModel):
    name: str
    status: TelegramConnection
    is_connect: bool
    
