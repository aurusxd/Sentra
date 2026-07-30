"""add max operator session

Revision ID: c3f8d2e71a40
Revises: b7e4a1c29d63
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c3f8d2e71a40"
down_revision: Union[str, Sequence[str], None] = "b7e4a1c29d63"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dialogs", sa.Column("max_operator_chat_id", sa.String(255), nullable=True))
    op.add_column("dialogs", sa.Column("max_operator_user_id", sa.String(255), nullable=True))
    op.add_column(
        "dialogs",
        sa.Column("max_admin_notification_message_id", sa.String(255), nullable=True),
    )
    op.create_index(
        "ix_dialogs_max_operator_chat_id",
        "dialogs",
        ["max_operator_chat_id"],
        unique=False,
    )
    op.create_index(
        "ix_dialogs_max_admin_notification_message_id",
        "dialogs",
        ["max_admin_notification_message_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_dialogs_max_admin_notification_message_id", table_name="dialogs")
    op.drop_index("ix_dialogs_max_operator_chat_id", table_name="dialogs")
    op.drop_column("dialogs", "max_admin_notification_message_id")
    op.drop_column("dialogs", "max_operator_user_id")
    op.drop_column("dialogs", "max_operator_chat_id")
