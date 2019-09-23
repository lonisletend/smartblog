# encoding: utf-8
from app import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    priority = db.Column(db.Integer)
    description = db.Column(db.String(512))
    is_shown = db.Column(db.Integer, default=1)   # 1=展示  2=隐藏
    is_deleted = db.Column(db.Integer, default=0)