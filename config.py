# encoding: utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 首页最大文章数，超过分页
    POSTS_PER_PAGE = 8

    #文章编辑页最大文章数，超过分页
    POSTS_PER_PAGE_EDIT = 10

    # 访问记录页最大记录数，超过分页
    RECORDS_PER_PAGE = 25

    # 全文索引
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')