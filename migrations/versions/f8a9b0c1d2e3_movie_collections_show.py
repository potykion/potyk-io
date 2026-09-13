"""Add movie_collections.show; hide watch_later and mash lists from page.

Подборки «Посмотреть позже» и «Посмотреть с Маш» остаются в рулетке,
но не показываются под «Подборочки».
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f8a9b0c1d2e3"
down_revision: Union[str, Sequence[str], None] = "e9f0a1b2c3d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

HIDDEN_COLLECTION_IDS = ("watch_later", "посмотреть-с-маш")


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "movie_collections" not in insp.get_table_names():
        return

    columns = {column["name"] for column in insp.get_columns("movie_collections")}
    if "show" not in columns:
        with op.batch_alter_table("movie_collections") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "show",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.text("1"),
                )
            )

    bind.execute(
        sa.text(
            "UPDATE movie_collections SET show = 0 WHERE id = :id OR title = :title"
        ),
        {"id": "watch_later", "title": "Посмотреть позже"},
    )
    bind.execute(
        sa.text(
            "UPDATE movie_collections SET show = 0 WHERE id = :id OR title = :title"
        ),
        {"id": "посмотреть-с-маш", "title": "Посмотреть с Маш"},
    )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "movie_collections" not in insp.get_table_names():
        return

    columns = {column["name"] for column in insp.get_columns("movie_collections")}
    if "show" not in columns:
        return

    with op.batch_alter_table("movie_collections") as batch_op:
        batch_op.drop_column("show")
