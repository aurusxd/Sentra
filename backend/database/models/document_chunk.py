from datetime import datetime

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.models.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)

    knowledge_file_id: Mapped[int] = mapped_column(
        ForeignKey(
            "knowledge_files.id",
            ondelete="CASCADE",
        )
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey(
            "employees.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    chunk_index: Mapped[int]

    text: Mapped[str] = mapped_column(Text)

    embedding_id: Mapped[str | None]

    created_at: Mapped[datetime]