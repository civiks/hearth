"""add review table

Revision ID: f7a1c3d5e9b2
Revises: e5f6a7b8c9d0
Create Date: 2026-06-04 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f7a1c3d5e9b2"
down_revision: str | Sequence[str] | None = "e5f6a7b8c9d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "review" in inspector.get_table_names():
        return
    op.create_table(
        "review",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("professional_id", sa.Integer(), nullable=True),
        sa.Column("request_id", sa.Integer(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=False),
        sa.Column("comment", sa.String(length=500), nullable=True),
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["service_id"], ["service.id"]),
        sa.ForeignKeyConstraint(["author_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["professional_id"], ["service_professional.id"]),
        sa.ForeignKeyConstraint(["request_id"], ["service_request.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_review_service_id", "review", ["service_id"])
    op.create_index("ix_review_author_id", "review", ["author_id"])
    op.create_index("ix_review_professional_id", "review", ["professional_id"])
    op.create_index("ix_review_date_created", "review", ["date_created"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "review" not in inspector.get_table_names():
        return
    op.drop_table("review")
