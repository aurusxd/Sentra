from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.database.enums import KnowledgeFileStatus


class KnowledgeFileUpload(BaseModel):
    """
    Пока пустая схема.

    Сам файл приходит через UploadFile,
    поэтому Pydantic здесь не нужен.
    """

    pass


class KnowledgeFileRead(BaseModel):
    id: int

    employee_id: int

    original_filename: str

    stored_filename: str

    mime_type: str | None

    size_bytes: int

    status: KnowledgeFileStatus

    error_message: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class KnowledgeFileList(BaseModel):
    files: list[KnowledgeFileRead]


class KnowledgeFileStatusUpdate(BaseModel):
    status: KnowledgeFileStatus