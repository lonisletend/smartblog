from app import db
from datetime import datetime

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    text = db.Column(db.String(16000000))
    cate_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    created = db.Column(db.DateTime, index=True, default=datetime.now)
    modified = db.Column(db.DateTime, index=True, default=datetime.now)
    is_topping = db.Column(db.Integer, index=True, default=0)  # 0=不置顶  1=置顶
    status = db.Column(db.Integer, index=True, default=1)  # 0=hidden, 1=publish, 2=draft
    views = db.Column(db.Integer, default=0)  #阅读量
    comments_num = db.Column(db.Integer, default=0) #评论数
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #作者
    is_deleted = db.Column(db.Integer, default=0)
    