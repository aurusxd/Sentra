from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.enums import DialogStatus
from backend.database.models.base import Base

if TYPE_CHECKING:
    from backend.database.models.channel import Channel
    from backend.database.models.employee import Employee
    from backend.database.models.message import Message


class Dialog(Base):
    __tablename__ = "dialogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    channel_id: Mapped[int | None] = mapped_column(
        ForeignKey("channels.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # id клиента в конкретном канале. Например telegram_user_id.
    client_external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    client_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    client_username: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[DialogStatus] = mapped_column(
        String(50),
        default=DialogStatus.ACTIVE,
        nullable=False,
    )

    is_human_takeover: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    employee: Mapped["Employee"] = relationship(back_populates="dialogs")
    channel: Mapped["Channel"] = relationship(back_populates="dialogs")

    messages: Mapped[list["Message"]] = relationship(
        back_populates="dialog",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "channel_id",
            "client_external_id",
            name="uq_dialog_employee_channel_client",
        ),
    )