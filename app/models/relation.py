from app import db

class Relation(db.Model):
    __tablename__ = 'relation',
    art_id = db.Column(db.Integer, db.ForeignKey('article.id'), primary_key=True),
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    is_deleted = db.Column(db.Integer, default=0)