from app import db
from datetime import datetime

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    art_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)
    username = db.Column(db.String(32))
    time = db.Column(db.DateTime, index=True, default=datetime.now)
    ip = db.Column(db.String(32))
    platform = db.Column(db.String(32))
    browser = db.Column(db.String(32))
    version = db.Column(db.String(32))
    language = db.Column(db.String(32))
    is_deleted = db.Column(db.Integer, default=0)
