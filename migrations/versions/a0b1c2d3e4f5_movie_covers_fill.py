"""Fill missing movie covers from local poster files.

Для всех movies без cover проставляет путь к постеру в static/potyk-io/img/movies/
(скачаны с CDN Кинопоиска по kinopoisk id).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a0b1c2d3e4f5"
down_revision: Union[str, Sequence[str], None] = "f8a9b0c1d2e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# id -> /static/potyk-io/img/movies/...
COVERS: dict[str, str] = {
    "105813": "/static/potyk-io/img/movies/beyond.jpg",
    "10646404": "/static/potyk-io/img/movies/ruster.jpg",
    "1068448": "/static/potyk-io/img/movies/otsepenevshie-ot-strakha.jpg",
    "1112153": "/static/potyk-io/img/movies/psikhiatricheskaya-bolnitsa-kondzhiam.jpg",
    "1148990": "/static/potyk-io/img/movies/glotay.jpg",
    "11979274": "/static/potyk-io/img/movies/pasha-tekhnik-za-kem-stoit-andegraund.jpg",
    "1198736": "/static/potyk-io/img/movies/ya-idu-iskat.jpg",
    "1219852": "/static/potyk-io/img/movies/dumayu-kak-vse-zakonchit.jpg",
    "1343318": "/static/potyk-io/img/movies/razdelenie.jpg",
    "1394680": "/static/potyk-io/img/movies/stseny-iz-supruzheskoy-zhizni.jpg",
    "1395841": "/static/potyk-io/img/movies/chelovek-iz-podolska.jpg",
    "1405778": "/static/potyk-io/img/movies/execution.jpg",
    "17331": "/static/potyk-io/img/movies/another-day-in-paradise.jpg",
    "2000102": "/static/potyk-io/img/movies/kiberpank-begushchie-po-krayu.jpg",
    "222209": "/static/potyk-io/img/movies/masha.jpg",
    "257376": "/static/potyk-io/img/movies/berserk.jpg",
    "258687": "/static/potyk-io/img/movies/interstellar.jpg",
    "262771": "/static/potyk-io/img/movies/99-francs.jpg",
    "26501": "/static/potyk-io/img/movies/muzhskoe-zhenskoe.jpg",
    "273302": "/static/potyk-io/img/movies/mgla.jpg",
    "279596": "/static/potyk-io/img/movies/pineapple-express.jpg",
    "281752": "/static/potyk-io/img/movies/the-ex-drummer.jpg",
    "2868": "/static/potyk-io/img/movies/eys-ventura-rozysk-domashnikh-zhivotnykh.jpg",
    "2931": "/static/potyk-io/img/movies/high-art.jpg",
    "325465": "/static/potyk-io/img/movies/zhestokost.jpg",
    "325549": "/static/potyk-io/img/movies/bezzabotnaya.jpg",
    "325598": "/static/potyk-io/img/movies/reportazh.jpg",
    "3547": "/static/potyk-io/img/movies/fakultet.jpg",
    "35786": "/static/potyk-io/img/movies/obshchestvo.jpg",
    "362": "/static/potyk-io/img/movies/podvodnaya-lodka.jpg",
    "367": "/static/potyk-io/img/movies/requiem-for-a-dream.jpg",
    "374718": "/static/potyk-io/img/movies/monstro.jpg",
    "4385": "/static/potyk-io/img/movies/fear-and-loathing-in-las-vegas.jpg",
    "4396438": "/static/potyk-io/img/movies/bednye-neschastnye.jpg",
    "4411": "/static/potyk-io/img/movies/cheech-and-chong.jpg",
    "4455": "/static/potyk-io/img/movies/drugstore-cowboy.jpg",
    "467293": "/static/potyk-io/img/movies/filth.jpg",
    "469214": "/static/potyk-io/img/movies/bud-so-mnoy.jpg",
    "4807": "/static/potyk-io/img/movies/ne-grozi-yuzhnomu-tsentralu-popivaya-sok-u-sebya-v-kvartale.jpg",
    "4882": "/static/potyk-io/img/movies/the-panic-in-needle-park.jpg",
    "493098": "/static/potyk-io/img/movies/shkola.jpg",
    "495892": "/static/potyk-io/img/movies/astral.jpg",
    "5073923": "/static/potyk-io/img/movies/unrest.jpg",
    "5092": "/static/potyk-io/img/movies/stoned.jpg",
    "5106451": "/static/potyk-io/img/movies/byt-prisyazhnym.jpg",
    "5106807": "/static/potyk-io/img/movies/lozhka-sakhara.jpg",
    "515": "/static/potyk-io/img/movies/trainspotting.jpg",
    "519": "/static/potyk-io/img/movies/chelovek-dozhdya.jpg",
    "5446941": "/static/potyk-io/img/movies/materialistka.jpg",
    "555": "/static/potyk-io/img/movies/bolshoy-lebovski.jpg",
    "55830": "/static/potyk-io/img/movies/christiane-f.jpg",
    "57336": "/static/potyk-io/img/movies/schaste.jpg",
    "590022": "/static/potyk-io/img/movies/sinister.jpg",
    "5932": "/static/potyk-io/img/movies/ochen-strashnoe-kino.jpg",
    "6012599": "/static/potyk-io/img/movies/odna-iz-mnogikh.jpg",
    "6103378": "/static/potyk-io/img/movies/svodish-s-uma.jpg",
    "6137": "/static/potyk-io/img/movies/lyubovnyy-napitok-9.jpg",
    "6175": "/static/potyk-io/img/movies/the-basketball-diaries.jpg",
    "63912": "/static/potyk-io/img/movies/ukroshchenie-stroptivogo.jpg",
    "6733": "/static/potyk-io/img/movies/sid-and-nancy.jpg",
    "7088374": "/static/potyk-io/img/movies/odno-tseloe.jpg",
    "714248": "/static/potyk-io/img/movies/pesn-morya.jpg",
    "7229988": "/static/potyk-io/img/movies/ugly-sister.jpg",
    "724982": "/static/potyk-io/img/movies/zvezda.jpg",
    "7327911": "/static/potyk-io/img/movies/fekkhem-kholl.jpg",
    "7378605": "/static/potyk-io/img/movies/obitel-zla.jpg",
    "741214": "/static/potyk-io/img/movies/ptichiy-korob.jpg",
    "7421341": "/static/potyk-io/img/movies/kommersant.jpg",
    "744776": "/static/potyk-io/img/movies/t2-trainspotting.jpg",
    "7519616": "/static/potyk-io/img/movies/vykhod-8.jpg",
    "7525290": "/static/potyk-io/img/movies/dvoe-v-odnoy-zhizni-ne-schitaya-sobaki.jpg",
    "7576": "/static/potyk-io/img/movies/naked-lunch.jpg",
    "7701": "/static/potyk-io/img/movies/sex-lies-and-videotape.jpg",
    "77202": "/static/potyk-io/img/movies/mesto-vstrechi-izmenit-nelzya.jpg",
    "78871": "/static/potyk-io/img/movies/silent-hill.jpg",
    "8134": "/static/potyk-io/img/movies/blair-witch-project.jpg",
    "819101": "/static/potyk-io/img/movies/omerzitelnaya-vosmerka.jpg",
    "820": "/static/potyk-io/img/movies/sekretarsha.jpg",
    "8366": "/static/potyk-io/img/movies/nechto.jpg",
    "839954": "/static/potyk-io/img/movies/legenda.jpg",
    "88190": "/static/potyk-io/img/movies/candy.jpg",
    "9691": "/static/potyk-io/img/movies/besslavnye-ublyudki.jpg",
}


def upgrade() -> None:
    bind = op.get_bind()
    for movie_id, cover in COVERS.items():
        bind.execute(
            sa.text(
                "UPDATE movies SET cover = :cover "
                "WHERE id = :id AND (cover IS NULL OR cover = '')"
            ),
            {"id": movie_id, "cover": cover},
        )


def downgrade() -> None:
    bind = op.get_bind()
    for movie_id in COVERS:
        bind.execute(
            sa.text("UPDATE movies SET cover = NULL WHERE id = :id"),
            {"id": movie_id},
        )
