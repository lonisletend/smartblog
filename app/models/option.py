from app import db

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    value = db.Column(db.String(64))
    is_deleted = db.Column(db.Integer, default=0)