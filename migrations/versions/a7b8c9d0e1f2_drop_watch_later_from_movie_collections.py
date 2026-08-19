"""Drop watch_later flag from movie_collections.

Рулетка теперь работает по всем подборкам, поэтому специальный признак
`watch_later` больше не нужен. Перед удалением колонки нормализуем данные:
оставляем коллекцию `watch_later` обычной коллекцией и снимаем флаг у всех строк.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = "f2a3b4c5d6e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

WATCH_LATER_INDEX = "ix_movie_collections_watch_later"


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if "movie_collections" not in insp.get_table_names():
        return

    columns = {column["name"] for column in insp.get_columns("movie_collections")}
    if "watch_later" not in columns:
        return

    bind.execute(sa.text("UPDATE movie_collections SET watch_later = 0"))

    indexes = {index["name"] for index in insp.get_indexes("movie_collections")}
    if WATCH_LATER_INDEX in indexes:
        op.drop_index(WATCH_LATER_INDEX, table_name="movie_collections")

    with op.batch_alter_table("movie_collections") as batch_op:
        batch_op.drop_column("watch_later")


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if "movie_collections" not in insp.get_table_names():
        return

    columns = {column["name"] for column in insp.get_columns("movie_collections")}
    if "watch_later" in columns:
        return

    with op.batch_alter_table("movie_collections") as batch_op:
        batch_op.add_column(
            sa.Column(
                "watch_later",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )

    op.create_index(WATCH_LATER_INDEX, "movie_collections", ["watch_later"], unique=False)
