# encoding: utf-8
from app import db
from datetime import datetime
# from app.models import searchableMixin
from app.models.searchableMixin import SearchableMixin
# from app.models import relation
# from app.models import tag

class Article(SearchableMixin, db.Model):
    __searchable__ = ['text']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    text = db.Column(db.String(16000000))
    cate_id = db.Column(db.Integer)
    created = db.Column(db.DateTime, index=True, default=datetime.now)
    modified = db.Column(db.DateTime, index=True, default=datetime.now)
    is_topping = db.Column(db.Integer, index=True, default=0)  # 0=不置顶  1=置顶
    status = db.Column(db.Integer, index=True, default=1)  # 0=hidden, 1=publish, 2=draft
    views = db.Column(db.Integer, default=0)  #阅读量
    comments_num = db.Column(db.Integer, default=0) #评论数
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #作者
    wordcloud = db.Column(db.String(10240)) # 词云数据 json字符串
    is_deleted = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return '<Article {}>'.format(self.title)
