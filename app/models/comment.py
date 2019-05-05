# encoding: utf-8
from app import db
from datetime import datetime

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    art_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)
    username = db.Column(db.String(32))
    text = db.Column(db.String(512))
    created = db.Column(db.DateTime, index=True, default=datetime.now)
    status = db.Column(db.Integer, index=True, default=1)  # 0=hidden, 1=show
    is_deleted = db.Column(db.Integer, default=0)

    def asdict(self):
        return {'id': self.id, 'art_id': self.art_id, 'username': self.username, \
                'text': self.text, 'created': self.created.strftime("%Y-%m-%d %H:%M")}