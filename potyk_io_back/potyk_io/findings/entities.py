from datetime import datetime

from potyk_io_back.core.db import db


class Finding(db.Model):
    __tablename__ = "findings"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1024), nullable=False, unique=True, index=True)
    title = db.Column(db.String(512), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
    watched_at = db.Column(db.DateTime, nullable=True, index=True)

    @property
    def is_watched(self) -> bool:
        return self.watched_at is not None
