from os import environ as env
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .database import DbConfig

load_dotenv()

OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY")
API_URL=os.getenv("API_URL")
TOKEN_ENCRYPTION_KEY=os.getenv("TOKEN_ENCRYPTION_KEY")
TELEGRAM_LEAD_BOT_TOKEN=os.getenv("TELEGRAM_LEAD_BOT_TOKEN")
TELEGRAM_LEAD_CHAT_ID=os.getenv("TELEGRAM_LEAD_CHAT_ID")
class Config(BaseModel):
    database: DbConfig = Field(default_factory=lambda: DbConfig(**env))


config = Config()
