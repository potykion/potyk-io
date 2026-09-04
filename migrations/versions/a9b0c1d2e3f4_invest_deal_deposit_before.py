"""invest deal deposit_before on close

Revision ID: a9b0c1d2e3f4
Revises: f7a8b9c0d1e2
Create Date: 2026-09-04 13:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a9b0c1d2e3f4"
down_revision: Union[str, Sequence[str], None] = "f7a8b9c0d1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("invest_deals", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("deposit_before", sa.Numeric(precision=18, scale=2), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("invest_deals", schema=None) as batch_op:
        batch_op.drop_column("deposit_before")
