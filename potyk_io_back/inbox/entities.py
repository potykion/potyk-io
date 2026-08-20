from datetime import datetime

from potyk_io_back.core.db import db


class Issue(db.Model):
    __tablename__ = "issues"

    id = db.Column(db.Integer, primary_key=True)
    project = db.Column(db.String(64), nullable=False, index=True)
    status = db.Column(db.String(16), nullable=False, default="new", index=True)
    text = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project": self.project,
            "status": self.status,
            "text": self.text,
            "created_at": self.created_at.isoformat(timespec="seconds")
            if self.created_at
            else None,
        }
