"""security constraints

Revision ID: 9a7c2f41b8d0
Revises: 41237f34dc50
"""

from typing import Sequence, Union

from alembic import op

revision: str = "9a7c2f41b8d0"
down_revision: Union[str, Sequence[str], None] = "41237f34dc50"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_users_name", "users", ["name"], unique=True)
    op.execute(
        """
        DELETE FROM messages older
        USING messages newer
        WHERE older.id < newer.id
          AND older.dialog_id = newer.dialog_id
          AND older.sender_type = newer.sender_type
          AND older.external_message_id = newer.external_message_id
          AND older.external_message_id IS NOT NULL
        """
    )
    op.create_unique_constraint(
        "uq_message_dialog_sender_external",
        "messages",
        ["dialog_id", "sender_type", "external_message_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_message_dialog_sender_external", "messages", type_="unique")
    op.drop_index("ix_users_name", table_name="users")
