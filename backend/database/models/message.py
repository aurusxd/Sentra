from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.enums import SenderType
from backend.database.models.base import Base

if TYPE_CHECKING:
    from backend.database.models.dialog import Dialog

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    dialog_id: Mapped[int] = mapped_column(
        ForeignKey("dialogs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sender_type: Mapped[SenderType] = mapped_column(String(50), nullable=False)

    text: Mapped[str] = mapped_column(Text, nullable=False)

    # id сообщения во внешнем канале. Например telegram message_id.
    external_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    dialog: Mapped["Dialog"] = relationship(back_populates="messages")

    __table_args__ = (
        UniqueConstraint(
            "dialog_id",
            "sender_type",
            "external_message_id",
            name="uq_message_dialog_sender_external",
        ),
    )
