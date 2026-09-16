from datetime import datetime

from potyk_io_back.core.db import db


class NoteVote(db.Model):
    __tablename__ = "note_votes"

    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.String(512), nullable=False, index=True)
    note_url = db.Column(db.String(1024), nullable=False)
    title = db.Column(db.String(512), nullable=False, default="")
    vote = db.Column(db.String(16), nullable=False, index=True)  # like | dislike
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
