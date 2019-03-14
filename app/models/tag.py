from app import db
from app.models import relation
from app.models import article

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    is_deleted = db.Column(db.Integer, default=0)