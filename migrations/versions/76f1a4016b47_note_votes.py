"""note_votes: лайки/дизлайки заметок из «Свайпать страницы»

Revision ID: 76f1a4016b47
Revises: c4d5e6f7a8b9
Create Date: 2026-09-16 13:10:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "76f1a4016b47"
down_revision: Union[str, Sequence[str], None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "note_votes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("note_id", sa.String(length=512), nullable=False),
        sa.Column("note_url", sa.String(length=1024), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("vote", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_note_votes_note_id"), "note_votes", ["note_id"], unique=False)
    op.create_index(op.f("ix_note_votes_vote"), "note_votes", ["vote"], unique=False)
    op.create_index(
        op.f("ix_note_votes_created_at"), "note_votes", ["created_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_note_votes_created_at"), table_name="note_votes")
    op.drop_index(op.f("ix_note_votes_vote"), table_name="note_votes")
    op.drop_index(op.f("ix_note_votes_note_id"), table_name="note_votes")
    op.drop_table("note_votes")
