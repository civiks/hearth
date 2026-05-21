"""marketplace fields (avatar/image/rating/review_count)

Revision ID: 9b2f3a17c4d1
Revises: 58c0bdb13b70
Create Date: 2026-05-20 23:45:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9b2f3a17c4d1"
down_revision: str | Sequence[str] | None = "58c0bdb13b70"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _has_column(inspector, table: str, column: str) -> bool:
    return column in {c["name"] for c in inspector.get_columns(table)}


def upgrade() -> None:
    # Tolerate partial state (e.g. someone manually added a subset of these
    # columns before the migration ran). Idempotent per column.
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _has_column(inspector, "user", "avatar_url"):
        op.add_column("user", sa.Column("avatar_url", sa.String(length=255), nullable=True))
    if not _has_column(inspector, "user", "rating"):
        op.add_column("user", sa.Column("rating", sa.Float(), nullable=True))
    if not _has_column(inspector, "user", "review_count"):
        op.add_column("user", sa.Column("review_count", sa.Integer(), nullable=True))

    if not _has_column(inspector, "service", "image_url"):
        op.add_column("service", sa.Column("image_url", sa.String(length=500), nullable=True))
    if not _has_column(inspector, "service", "rating"):
        op.add_column("service", sa.Column("rating", sa.Float(), nullable=True))
    if not _has_column(inspector, "service", "review_count"):
        op.add_column("service", sa.Column("review_count", sa.Integer(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _has_column(inspector, "service", "review_count"):
        op.drop_column("service", "review_count")
    if _has_column(inspector, "service", "rating"):
        op.drop_column("service", "rating")
    if _has_column(inspector, "service", "image_url"):
        op.drop_column("service", "image_url")

    if _has_column(inspector, "user", "review_count"):
        op.drop_column("user", "review_count")
    if _has_column(inspector, "user", "rating"):
        op.drop_column("user", "rating")
    if _has_column(inspector, "user", "avatar_url"):
        op.drop_column("user", "avatar_url")
