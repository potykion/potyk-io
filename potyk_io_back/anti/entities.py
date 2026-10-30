from datetime import datetime

from potyk_io_back.core.db import db


class AntiPost(db.Model):
    __tablename__ = "anti_posts"

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
