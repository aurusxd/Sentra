"""add max admin chat id

Revision ID: b7e4a1c29d63
Revises: 9a7c2f41b8d0
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b7e4a1c29d63"
down_revision: Union[str, Sequence[str], None] = "9a7c2f41b8d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "employees",
        sa.Column("max_admin_chat_id", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("employees", "max_admin_chat_id")
