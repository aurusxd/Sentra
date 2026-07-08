from __future__ import annotations
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database.enums import ChannelStatus, ChannelType
from backend.database.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.database.models.employee import Employee
    from backend.database.models.dialog import Dialog


class Channel(Base):
    """
    Универсальная таблица каналов.
    Сейчас будет только Telegram, но потом сюда можно добавить website, whatsapp и т.д.
    """

    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type: Mapped[ChannelType] = mapped_column(String(50), nullable=False)

    status: Mapped[ChannelStatus] = mapped_column(
        String(50),
        default=ChannelStatus.DISCONNECTED,
        nullable=False,
    )

    # Например telegram bot_id.
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # Например @my_support_bot.
    external_username: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Для Telegram здесь можно хранить зашифрованный bot token.
    token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)

    webhook_secret: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    connected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    employee: Mapped["Employee"] = relationship(back_populates="channels")

    dialogs: Mapped[list["Dialog"]] = relationship(
        back_populates="channel",
    )

    __table_args__ = (
        UniqueConstraint("type", "external_id", name="uq_channel_type_external_id"),
    )
