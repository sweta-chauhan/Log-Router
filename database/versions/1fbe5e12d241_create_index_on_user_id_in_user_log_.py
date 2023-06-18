"""create index on user_id in user_log table

Revision ID: 1fbe5e12d241
Revises: 4c3482859dd8
Create Date: 2023-06-18 01:37:36.122611

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1fbe5e12d241"
down_revision = "4c3482859dd8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("idx_log_user_id", "user_log", ["user_id"])


def downgrade() -> None:
    op.drop_index("idx_log_user_id", "user_log")
