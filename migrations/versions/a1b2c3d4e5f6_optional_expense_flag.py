"""optional expense flag

Revision ID: a1b2c3d4e5f6
Revises: 78517d14a163
Create Date: 2026-08-17 13:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "78517d14a163"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("expenses", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("optional", sa.Boolean(), nullable=False, server_default=sa.false())
        )


def downgrade() -> None:
    with op.batch_alter_table("expenses", schema=None) as batch_op:
        batch_op.drop_column("optional")
