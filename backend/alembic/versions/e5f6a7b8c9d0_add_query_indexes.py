"""add indexes on hot-path query columns

Revision ID: e5f6a7b8c9d0
Revises: c4d8e2f1a9b3
Create Date: 2026-05-31 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: str | Sequence[str] | None = "c4d8e2f1a9b3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_INDEXES = [
    ("ix_service_request_customer_id", "service_request", ["customer_id"]),
    ("ix_service_request_service_id", "service_request", ["service_id"]),
    ("ix_service_request_service_status", "service_request", ["service_status"]),
    ("ix_service_request_date_of_request", "service_request", ["date_of_request"]),
    ("ix_service_professional_user_id", "service_professional", ["user_id"]),
    ("ix_service_professional_service_id", "service_professional", ["service_id"]),
]


def _existing_indexes(inspector, table: str) -> set[str]:
    return {idx["name"] for idx in inspector.get_indexes(table)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for name, table, columns in _INDEXES:
        if name not in _existing_indexes(inspector, table):
            op.create_index(name, table, columns)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for name, table, _ in _INDEXES:
        if name in _existing_indexes(inspector, table):
            op.drop_index(name, table_name=table)
