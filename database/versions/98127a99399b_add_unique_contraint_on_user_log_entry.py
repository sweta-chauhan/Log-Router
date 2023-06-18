"""add unique contraint on user log entry

Revision ID: 98127a99399b
Revises: 1fbe5e12d241
Create Date: 2023-06-18 01:37:59.975506

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "98127a99399b"
down_revision = "1fbe5e12d241"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uid", "user_log", ["unix_ts", "user_id", "event_name"])


def downgrade() -> None:
    op.drop_constraint("uid", "user_log")
