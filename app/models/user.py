from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    password = db.Column(db.String(128)) #hash
    email = db.Column(db.String(128), index=True, unique=True)
    about_me = db.Column(db.String(256))
    created = db.Column(db.DateTime, index=True, default=datetime.now)
    logged = db.Column(db.DateTime, index=True, default=datetime.now)
    role = db.Column(db.String(16), index=True, default='vistor')   #admin
    is_deleted = db.Column(db.Integer, default=0) # 0=未删除， 1=已删除
    
    def __repr__(self):
        return '<User {}>'.format(self.username) 