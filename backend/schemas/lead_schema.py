from pydantic import BaseModel, Field


class LeadCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=1, max_length=50)
    telegram: str = Field(min_length=1, max_length=100)
    website: str = Field(default="", max_length=200)


class LeadResponse(BaseModel):
    ok: bool
