from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.enums import EmployeeStatus
from backend.database.models.base import Base

if TYPE_CHECKING:
    from backend.database.models.channel import Channel
    from backend.database.models.dialog import Dialog
    from backend.database.models.user import User
    from backend.database.models.knowledge_file import KnowledgeFile


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)

    business_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    language: Mapped[str] = mapped_column(String(50), default="ru", nullable=False)
    tone: Mapped[str] = mapped_column(String(100), default="friendly", nullable=False)

    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    fallback_message: Mapped[str] = mapped_column(
        Text,
        default="Я не нашел точной информации. Передам ваш вопрос менеджеру.",
        nullable=False,
    )

    telegram_admin_chat_id: Mapped[str | None] = mapped_column(
        nullable=True,
    )
    status: Mapped[EmployeeStatus] = mapped_column(
        String(50),
        default=EmployeeStatus.NEEDS_SETUP,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    is_deleted: Mapped[Boolean] = mapped_column(Boolean,default=False)

    owner: Mapped["User"] = relationship(back_populates="employees")

    knowledge_files: Mapped[list["KnowledgeFile"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan",
    )

    channels: Mapped[list["Channel"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan",
    )

    dialogs: Mapped[list["Dialog"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan",
    )
