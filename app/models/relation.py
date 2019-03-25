# encoding: utf-8
from app import db

class Relation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    art_id = db.Column(db.Integer)
    tag_id = db.Column(db.Integer)
    is_deleted = db.Column(db.Integer, default=0)