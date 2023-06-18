"""log table

Revision ID: 4c3482859dd8
Revises:
Create Date: 2023-06-18 01:36:28.603039

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4c3482859dd8"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_log",
        sa.Column("uid", sa.String(64), nullable=False, primary_key=True),
        sa.Column("log_id", sa.Integer, nullable=False),
        sa.Column("unix_ts", sa.Integer, nullable=False),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("event_name", sa.String(8), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("user_log")
