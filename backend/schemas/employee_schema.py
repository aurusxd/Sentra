
from pydantic import BaseModel

class EmployeeCreate(BaseModel):
    name: str
    role: str
    business_description: str | None = None
    language: str = "ru"
    tone: str = "friendly"
    instruction: str
    fallback_message: str


class EmployeeUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    business_description: str | None = None
    language: str | None = None
    tone: str | None = None
    instruction: str | None = None
    fallback_message: str | None = None


class EmployeeRead(BaseModel):
    id: int
    name: str
    role: str
    language: str
    tone: str

    model_config = {
        "from_attributes": True
    }


