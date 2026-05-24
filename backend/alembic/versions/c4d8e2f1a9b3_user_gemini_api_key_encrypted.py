"""user.gemini_api_key_encrypted — BYOK Gemini key, Fernet-encrypted

Revision ID: c4d8e2f1a9b3
Revises: 9b2f3a17c4d1
Create Date: 2026-05-24 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4d8e2f1a9b3"
down_revision: str | Sequence[str] | None = "9b2f3a17c4d1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _has_column(inspector, table: str, column: str) -> bool:
    return column in {c["name"] for c in inspector.get_columns(table)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not _has_column(inspector, "user", "gemini_api_key_encrypted"):
        op.add_column(
            "user",
            sa.Column("gemini_api_key_encrypted", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _has_column(inspector, "user", "gemini_api_key_encrypted"):
        op.drop_column("user", "gemini_api_key_encrypted")
