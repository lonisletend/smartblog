# encoding: utf-8
import os
import re
import copy
import json
import time
from datetime import datetime, timedelta, date
from jieba import analyse, cut
from app import app
from app import db
from flask import render_template, request, jsonify, redirect, url_for, g
from sqlalchemy import or_
from app.forms.login_form import LoginForm
from app.forms.registeration_form import RegistrationForm
from flask_login import current_user, login_user, login_required, logout_user
from app.models.user import User
from app.models.category import Category
from app.models.article import Article
from app.models.tag import Tag
from app.models.relation import Relation
from app.models.comment import Comment
from app.models.record import Record
from app.models.option import Option


def is_del(obj):
    if obj.is_deleted==1:
        return True

@app.before_request
def before_request():
    if not hasattr(g,'blog_name'):
        blog_name = Option.query.filter_by(name='blog_name').first()
        if blog_name is not None:
            setattr(g,'blog_name',blog_name.value)
        else:
            setattr(g,'blog_name','SmartBlog')
    if not hasattr(g, 'loginForm'):
        setattr(g, 'loginForm', LoginForm())
    if not hasattr(g, 'registrationForm'):
        setattr(g, 'registrationForm', RegistrationForm())
    if not hasattr(g, 'sense_dict_list'):
        setattr(g, 'sense_dict_list', None)

# 首页
@app.route('/')
@app.route('/index')
def index():
    cateId = 0
    # 导航栏
    cates = get_categorys()
    #文章分页
    page = request.args.get('page', 1, type=int)
    # 处理文章信息
    if current_user.is_authenticated and current_user.mark is not None:
        # 当前用户已认证 + 当前用户有推荐数据（mark）
        page_size = app.config['POSTS_PER_PAGE']
        start_index = (page-1)*page_size
        end_index = start_index+page_size
        articles = Article.query.filter_by(status=1, is_deleted=0).order_by(Article.created.desc()).all()
        article_list = get_article_list_by_weight(articles, current_user.id)
        # 对获取的文章信息按权重倒序排序 取出所需的文章
        article_list.sort(key=lambda art: art['weight'], reverse=True)
        article_list = article_list[start_index: end_index]
        # 手动设置上下页链接
        next_url = url_for('index', page=page+1) \
            if len(articles) > end_index else None
        prev_url = url_for('index', page=page-1) \
            if start_index > 0 else None
    else:
        #分页查出所有可见(1)文章+倒序
        arts = Article.query.filter_by(status=1, is_deleted=0).order_by(Article.created.desc()).paginate(
            page, app.config['POSTS_PER_PAGE'], False)
        # 设置上下页链接
        next_url = url_for('index', page=arts.next_num) \
            if arts.has_next else None
        prev_url = url_for('index', page=arts.prev_num) \
            if arts.has_prev else None
        article_list = get_article_list(arts.items)
        
    return render_template('blog/index.html', title="Index", cates=cates, activeId=cateId, 
                            loginForm=g.loginForm,registrationForm=g.registrationForm, articleList=article_list,
                            prev_url=prev_url, next_url=next_url, blog_name=g.blog_name)

def get_article_list(articles):
    article_list = []
    artdict = {'id':0, 'title':'', 'text':'', 'date':'', 'author':'', 'cateName':'', 'views':0, 'isTopping':0}
    for art in articles:
        artdict['id'] = art.id
        artdict['title'] = art.title
        artdict['text'] = art.text.replace('#', '').replace('```', '')[:200]
        artdict['date'] = art.created.strftime("%Y-%m-%d")
        user = User.query.filter_by(id=art.user_id).first()
        if user is not None:
            artdict['author'] = user.username
        artdict['views'] = art.views
        cate = Category.query.filter_by(id=art.cate_id).first()
        if cate is not None:
            artdict['cateName'] = cate.name
        artdict['isTopping'] = art.is_topping
        article_list.append(copy.deepcopy(artdict))
    return article_list

# 计算文章权重并返回文章信息 不排序
def get_article_list_by_weight(articles, user_id):
    article_list = []
    artdict = {'id':0, 'title':'', 'text':'', 'date':'', 'author':'', 'cateName':'', 'views':0, 'isTopping':0, 'weight':1.0}
    for art in articles:
        artdict['id'] = art.id
        artdict['title'] = art.title
        artdict['text'] = art.text.replace('#', '').replace('```', '')[:200]
        artdict['date'] = art.created.strftime("%Y-%m-%d")
        user = User.query.filter_by(id=art.user_id).first()
        if user is not None:
            artdict['author'] = user.username
        artdict['views'] = art.views
        cate = Category.query.filter_by(id=art.cate_id).first()
        if cate is not None:
            artdict['cateName'] = cate.name
        artdict['isTopping'] = art.is_topping
        artdict['weight'] = get_weight_of_article(user_id, art.id)

        article_list.append(copy.deepcopy(artdict))
    article_list.sort(key=lambda art: art['weight'], reverse=True)
    return article_list

# 计算文章对当前用户的权重
def get_weight_of_article(user_id, art_id):
    # 1-->1.2  2-->1.3  3-->1.5  a-->*0.66
    weight = 1.0
    user = User.query.filter_by(id=user_id, is_deleted=0).first()
    markstr = user.mark
    # 该用户没有推荐数据，权重全为1 （正常情况不会走到这里）
    if markstr is None:
        return 1.0
    # 获取推荐标签
    markstrlist = markstr.split(',')
    marklist = list(map(int, markstrlist))
    # 获取文章标签
    taglist = []
    relations= Relation.query.filter_by(art_id=art_id, is_deleted=0).all()
    tag_ids = [relation.tag_id for relation in relations]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    if tags is not None and len(tags)!=0:
        taglist = [tag.id for tag in tags]
    # 求交集
    ret = list(set(marklist).intersection(set(taglist)))  
    if len(ret)==3:
        weight = 1.5
    elif len(ret)==2:
        weight = 1.3
    elif len(ret)==1:
        weight = 1.2
    # 判断当前用户是否已经看过当前文章 若已看过 降低权重
    record = Record.query.filter_by(art_id=art_id, user_id=user_id, is_deleted=0).first()
    if record is not None:
        weight *= 0.66
    return weight


# 分类首页
@app.route('/category/<catename>')
def category(catename):
    # 查出分类id
    cateId = Category.query.filter_by(name=catename).first().id
    # 导航栏
    cates = get_categorys()
    #文章分页
    page = request.args.get('page', 1, type=int)

    #分页查出该分类所有可见(1)文章+倒序
    arts = Article.query.filter_by(cate_id=cateId, status=1, is_deleted=0).order_by(Article.created.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('category', catename=catename, page=arts.next_num) \
        if arts.has_next else None
    prev_url = url_for('category', catename=catename, page=arts.prev_num) \
        if arts.has_prev else None
    article_list = get_article_list(arts.items)

    return render_template('blog/index.html', title="Index", cates=cates, activeId=cateId, 
                            loginForm=g.loginForm, registrationForm=g.registrationForm, articleList=article_list,
                            prev_url=prev_url, next_url=next_url, blog_name=g.blog_name)


# 测试
@app.route('/test')
def test():
    return render_template('test/test.html')


@app.route('/editor')
def editor():
    return render_template('admin/editor.html')


# 文章详情
@app.route('/article/<artid>')
def article(artid):
    # 导航栏分类
    cates = get_categorys()
    # 添加访问记录 同文章登录用户6小时记录一次，防止评论刷新产生垃圾数据影响推荐标记生成结果准确性
    ignore = False
    if current_user.is_authenticated:
        now = int(time.time())
        start = datetime.fromtimestamp(now-6*3600)
        end = datetime.fromtimestamp(now)
        record = Record.query.filter(Record.rtime>=start, Record.rtime<=end).filter_by(art_id=artid, user_id=current_user.id, is_deleted=0).first()
        if record is not None:
            ignore = True

    if ignore == False:
        record = Record()
        record.art_id = artid
        if current_user.is_authenticated:
            record.user_id = current_user.id
            record.username = current_user.username
        # 获取访问信息
        info = get_reqinfo(request)
        record.ip = info['ip']
        record.platform = info['platform']
        record.browser = info['browser']
        record.version = info['version']
        record.language = info['language']
        db.session.add(record)
        db.session.commit()

    # 构造文章详情信息
    art = Article.query.filter_by(id=artid).first()
    article = {'id':0, 'title':'', 'text':'', 'date':'', 'author':'', 'cateName':'', 'tagNames':[], 'views':0, 'isTopping':0, 'cloud': ''}
    article['id'] = art.id
    article['title'] = art.title
    article['text'] = art.text
    article['date'] = art.created.strftime("%Y-%m-%d")
    user = User.query.filter_by(id=art.user_id).first()
    if user is not None:
        article['author'] = user.username
    article['views'] = art.views+1
    cate = Category.query.filter_by(id=art.cate_id).first()
    if cate is not None:
        article['cateName'] = cate.name
    res = Relation.query.filter_by(art_id=art.id, is_deleted=0).all()
    for re in res:
        tag = Tag.query.filter_by(id=re.tag_id).first()
        article['tagNames'].append(copy.deepcopy(tag.name))
    article['isTopping'] = art.is_topping
    article['cloud'] = art.wordcloud
    # 阅读数+1
    Article.query.filter_by(id=artid).update({
        'views': art.views+1
    })
    db.session.commit()

    #构造评论信息
    cmts = Comment.query.filter_by(art_id=artid, is_deleted=0).all()
    comments = []
    user = User()
    cmtinfo = Comment()
    cmtdict = {'user': user, 'comment': cmtinfo}
    for cmt in cmts:
        user1 = User.query.filter_by(id=cmt.user_id).first()
        cmtdict['user'] = user1
        cmtdict['comment'] = cmt
        comments.append(copy.deepcopy(cmtdict))

    return render_template('blog/article.html', title="Article", cates=cates, loginForm=g.loginForm, 
                            registrationForm=g.registrationForm, article=article, comments=comments, blog_name=g.blog_name)


# 添加评论
@app.route('/add_comment', methods=['POST', 'GET'])
def add_comment():
    art_id = request.form['art_id']
    comment = request.form['comment']
    if comment is None or art_id is None:
        return jsonify({'status': False, 'msg': '添加评论失败！'})
    # print(art_id)
    # print(comment)
    cmt = Comment()
    cmt.art_id = art_id
    cmt.user_id = current_user.id
    cmt.username = current_user.username
    cmt.text = sense_filter(comment)
    db.session.add(cmt)

    article = Article.query.filter_by(id=art_id).first()
    # 文章评论数+1
    Article.query.filter_by(id=art_id).update({
        'comments_num': article.comments_num+1
    })
    db.session.commit()
    return jsonify({'status': True, 'msg': '添加评论成功！'})


def get_sense_dict_list(file_path):
    filter_dict = []
    file = open(file_path)
    while 1:
        line = file.readline()
        if not line:
            break
        filter_dict.append(line.replace('\n',''))
    return filter_dict

def sense_filter(text):
    cut_list = list(cut(text, cut_all=False))
    if g.sense_dict_list is None:
        g.sense_dict_list = get_sense_dict_list('./app/jiebatest/sense.txt')
    sense_list = list(set(g.sense_dict_list).intersection(set(cut_list)))
    for word in sense_list:
        text = text.replace(word, '*'*len(word))
    return text

# 登录
@app.route('/login', methods=['POST', 'GET'])
def login():
    username = request.form['username']
    password = request.form['password']
    # print('username={}, password={}'.format(username, password))

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({'status': False, 'msg': '用户名或密码错误！'})
    db.session.add(user)
    user.logged = datetime.now()
    db.session.commit()
    login_user(user)
    return jsonify({'status': True, 'msg': '登录成功，正在跳转...'})


# 注册
@app.route('/register', methods=['POST', 'GET'])
def register():
    # if current_user.is_authenticated:
    #     return jsonify({'status': True, 'msg': '用户已登录'})
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return jsonify({'status': False, 'msg': '该用户名已存在！'})
    user = User.query.filter_by(email=email).first()
    if user is not None:
        return jsonify({'status': False, 'msg': '该邮箱已存在！'})
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'status': True, 'msg': '注册成功，正在跳转到登录页面...'})


# 退出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    # print(request.full_path)
    # return redirect(url_for('index'))
    return jsonify({'status': True})


# 个人信息
@app.route('/profile/<username>')
# @login_required
def profile(username):
    # loginForm = LoginForm()
    # registrationForm = RegistrationForm()
    cates = get_categorys()

    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_authenticated:
        comments = Comment.query.filter_by(user_id=user.id).all()
        auth = True
    else:
        comments = []
        auth = False
    return render_template('blog/profile.html', loginForm=g.loginForm, cates=cates, registrationForm=g.registrationForm,
                            user=user, comments=comments, auth=auth, blog_name=g.blog_name)


# 个人信息编辑
@app.route('/edit_profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    password = request.form['epassword']
    about_me = request.form['about-me']
    # print('pass={}, about={}'.format(password, about_me))
    if password is not None and password != '':
        current_user.set_password(password)
    if about_me is not None and about_me != '':
        current_user.about_me = about_me
    db.session.commit()
    return jsonify({'status': True, 'msg': ''})


# 后台首页
@app.route('/admin_index')
@login_required
def admin_index():
    if current_user.role == "admin":
        size = {"article": 0, "comment": 0, "category": 0, "tag": 0, "user": 0}
        size['article'] = Article.query.filter_by(is_deleted=0).count()
        size['comment'] = Comment.query.filter_by(is_deleted=0).count()
        size['category'] = Category.query.filter_by(is_deleted=0).count()
        size['tag'] = Tag.query.filter_by(is_deleted=0).count()
        size['user'] = User.query.filter_by(is_deleted=0).count()
        return render_template('admin/index.html', size=size)
    else:
        return redirect(url_for('index'))


# 文章管理
@app.route('/article_manage', methods=['POST', 'GET'])
@login_required
def article_manage():
    page = request.args.get('page', 1, type=int)

    #分页查出所有可见(1)文章+倒序
    arts = Article.query.filter_by(status=1, is_deleted=0).order_by(Article.created.desc()).paginate(
        page, app.config['POSTS_PER_PAGE_EDIT'], False)
    next_url = url_for('article_manage', page=arts.next_num) \
        if arts.has_next else None
    prev_url = url_for('article_manage', page=arts.prev_num) \
        if arts.has_prev else None
    articleList = []
    for art in arts.items:
        article = {'id':0, 'title':'', 'text':'', 'date':'', 'author':'', 'cateName':'', 'tagNames':[], 'views':0, 'isTopping':0}
        article['id'] = art.id
        article['title'] = art.title
        article['text'] = art.text
        article['date'] = art.created.strftime("%Y-%m-%d")
        user = User.query.filter_by(id=art.user_id).first()
        article['author'] = user.username
        article['views'] = art.views+1
        cate = Category.query.filter_by(id=art.cate_id).first()
        article['cateName'] = cate.name
        # artdict['tags'] = []
        res = Relation.query.filter_by(art_id=art.id, is_deleted=0).all()
        for re in res:
            tag = Tag.query.filter_by(id=re.tag_id).first()
            article['tagNames'].append(copy.deepcopy(tag.name))
        article['isTopping'] = art.is_topping
        articleList.append(copy.deepcopy(article))
    return render_template('admin/article_manage.html', articleList=articleList,
                            prev_url=prev_url, next_url=next_url)


# 评论管理
@app.route('/comment_manage', methods=['POST', 'GET'])
@login_required
def comment_manage():
    if current_user.role == 'vistor':
        return render_template('blog/index.html')
    
    page = request.args.get('page', 1, type=int)
    #分页查出所有可见(1)文章+倒序
    arts = Article.query.filter_by(status=1, is_deleted=0).order_by(Article.created.desc()).paginate(
        page, app.config['POSTS_PER_PAGE_EDIT'], False)
    next_url = url_for('comment_manage', page=arts.next_num) \
        if arts.has_next else None
    prev_url = url_for('comment_manage', page=arts.prev_num) \
        if arts.has_prev else None
    articleList = get_article_list(arts.items)
    return render_template('admin/comment_manage.html', articleList=articleList,
                            prev_url=prev_url, next_url=next_url)
    

# 获取评论数据
@app.route('/comment/<artid>', methods=['POST', 'GET'])
@login_required
def comment(artid):
    comments = Comment.query.filter_by(art_id=artid, is_deleted=0).all()
    if comments is not None:
        comments = list(comments)
        # data = json.dumps(comment.__dict__ for comment in comments)
        # print(comments)
        # print(type(comments))
        data = []
        for cmt in comments:
            data.append(json.dumps(cmt.asdict()))
        return jsonify({'status': True, 'msg': 'success', 'data':json.dumps(data)})
    return jsonify({'status': False, 'msg': 'None'})


# 删除评论
@app.route('/delcmt/<cmtid>', methods=['POST', 'GET'])
@login_required
def delcmt(cmtid):
    if current_user.role == 'vistor':
        return render_template('blog/index.html')
    comment = Comment.query.filter_by(id=cmtid).first()
    if comment is not None:
        Comment.query.filter_by(id=cmtid).update({
            'is_deleted': 0
        })
        db.session.commit()
        return jsonify({'status': True, 'msg': '所选评论已删除！'})
    return jsonify({'status': False, 'msg':'删除失败！'})

# 新建文章
@app.route('/admin_new', methods=['POST', 'GET'])
@login_required
def admin_new():
    if current_user.role == "vistor":
        return render_template('blog/index.html')
    else:
        if request.method == 'GET':
            cates = Category.query.filter_by(is_deleted=0).all()
            # for cate in cates:
            #     print("id={}, name={}".format(cate.id, cate.name))
            return render_template('admin/new.html', cates=cates)
        elif request.method == 'POST':

            title = request.form['title']
            tmpart = Article.query.filter_by(title=title).first()
            if tmpart is not None:
                return jsonify({'status': False, 'msg': '该标题已存在，请检查是否重复发布！'})
            article = Article()
            article.title = request.form['title']
            article.text = request.form['text']
            article.cate_id = request.form['category']
            article.is_topping = request.form['is_topping']
            article.status = request.form['status']
            article.user_id = current_user.id
            article.wordcloud = get_cloud(article.text)
            db.session.add(article)
            db.session.commit()
            tempArticle =  Article.query.filter_by(title=title).first()
            # tags

            ttags = eval(request.form['tags'][1:-1])
            # print(ttags)
            # print(type(ttags))
            #标签只有一个，eval转出来是dict,有多个，eval转出来是元素为dict的tuple，转换成list再进行统一操作
            tags = []
            if isinstance(ttags, dict):
                tags.append(ttags)
            else:
                tags = ttags
            # 标签存在则查出，不存在则添加，最后添加文章-标签关系
            for tag in tags:
                # print('tag={}'.format(tag))
                tagName = tag['value']
                tempTag = Tag.query.filter_by(name=tagName).first()
                if tempTag is None:
                    tempTag = Tag()
                    tempTag.name = tagName
                    db.session.add(tempTag)
                    # db.session.commit()
                    tempTag = Tag.query.filter_by(name=tagName).first()
                relation = Relation()
                relation.art_id = tempArticle.id
                # print('art_id={}'.format(relation.art_id))
                relation.tag_id = tempTag.id
                # print('tag_id={}'.format(relation.tag_id))
                db.session.add(relation)
                db.session.commit()

            return jsonify({'status': True, 'msg': '发布成功，点击跳转到文章详情页！', 'artid':tempArticle.id})


# 文章编辑
@app.route('/article_edit/<artid>', methods=['POST', 'GET'])
@login_required
def article_edit(artid):
    if request.method == 'GET':
        #返回文章详情信息
        art = Article.query.filter_by(id=artid).first()
        article = {'id':0, 'title':'', 'text':'', 'date':'', 'author':'', 'cateName':'', 'tagStr':'', 'views':0, 'isTopping':0, 'status':0}
        article['id'] = art.id
        article['title'] = art.title
        article['text'] = art.text
        article['date'] = art.created.strftime("%Y-%m-%d")
        user = User.query.filter_by(id=art.user_id).first()
        article['author'] = user.username
        article['views'] = art.views+1
        cate = Category.query.filter_by(id=art.cate_id).first()
        article['cateName'] = cate.name
        # artdict['tags'] = []
        tags = []
        res = Relation.query.filter_by(art_id=art.id, is_deleted=0).all()
        for re in res:
            tag = Tag.query.filter_by(id=re.tag_id).first()
            tags.append(copy.deepcopy(tag.name))
        article['tagStr'] = ','.join(tags)
        article['isTopping'] = art.is_topping
        article['status'] = art.status

        #所有可选分类
        cates = Category.query.filter_by(is_deleted=0).all()

        return render_template('admin/article_edit.html', article=article, cates=cates)

    elif request.method == 'POST':
        # artid = request.form['id']
        article = Article()
        article.title = request.form['title']
        article.text = request.form['text']
        article.cate_id = request.form['category']
        article.is_topping = request.form['is_topping']
        article.status = request.form['status']
        article.user_id = current_user.id
        article.wordcloud = get_cloud(article.text)
        Article.query.filter_by(id=artid).update({
            'title': article.title,
            'text':  article.text,
            'cate_id': article.cate_id,
            'is_topping': article.is_topping,
            'status': article.status,
            'wordcloud': article.wordcloud
        })
        db.session.commit()
        
        #删除当前文章-标签关系
        Relation.query.filter_by(art_id=artid).update({
            'is_deleted': 1
        })
        db.session.commit()

        ttags = eval(request.form['tags'][1:-1])
        # print(ttags)
        # print(type(ttags))
        #标签只有一个，eval转出来是dict,有多个，eval转出来是元素为dict的tuple，转换成list再进行统一操作
        tags = []
        if isinstance(ttags, dict):
            tags.append(ttags)
        else:
            tags = ttags
        # 标签存在则查出，不存在则添加，最后添加新的文章-标签关系
        for tag in tags:
            # print('tag={}'.format(tag))
            tagName = tag['value']
            tempTag = Tag.query.filter_by(name=tagName).first()
            if tempTag is None:
                tempTag = Tag()
                tempTag.name = tagName
                db.session.add(tempTag)
                # db.session.commit()
                tempTag = Tag.query.filter_by(name=tagName).first()
            relation = Relation()
            relation.art_id = artid
            # print('art_id={}'.format(relation.art_id))
            relation.tag_id = tempTag.id
            # print('tag_id={}'.format(relation.tag_id))
            db.session.add(relation)
            db.session.commit()

        return jsonify({'status': True, 'msg': '修改成功，点击跳转到文章详情页！', 'artid':artid})


# 文章删除
@app.route('/article_del/<artid>', methods=['POST', 'GET'])
@login_required
def article_del(artid):
    if current_user.role == "vistor":
        return render_template('blog/index.html')
    else:
        # artid = request.form['artid']
        if artid is not None:
            # print(artid)
            Article.query.filter_by(id=artid).update({
                'is_deleted': 1
            })
            db.session.commit()
            return jsonify({'status': True, 'msg': '删除成功！'})
        else:
            return jsonify({'status': False, 'msg': '删除失败！文章不存在！'})


# 分类管理
@app.route('/category_manage', methods=['POST', 'GET'])
@login_required
def category_manage():
    if current_user.role == "vistor":
        return render_template('blog/index.html')
    else:
        categorys = Category.query.filter_by(is_deleted=0).all()
        cate = {'id': 0, 'name': "", 'art_num': 0, 'is_shown': 1}
        cates = []
        for c in categorys:
            cate['id'] = c.id
            cate['name'] = c.name
            cate['art_num'] = Article.query.filter_by(cate_id=c.id, is_deleted=0).count()
            cate['is_shown'] = c.is_shown
            cates.append(copy.deepcopy(cate))

        return render_template('admin/category_manage.html', cates=cates)


# 分类添加
@app.route('/category_add', methods=['POST', 'GET'])
@login_required
def category_add():
    if current_user.role == "vistor":
        return render_template('blog/index.html')
    else:
        cateName = request.form['cate-name'].strip()
        print(cateName)
        category = Category.query.filter_by(name=cateName, is_deleted=0).first()
        if category is not None:
            return jsonify({'status': False, 'msg': '该分类已存在！'})
        else:
            # 存在已删除的，改为未删除
            category = Category.query.filter_by(name=cateName, is_deleted=1).first()
            if category is not None:
                Category.query.filter_by(id=category.id).update({
                    'is_deleted': 0
                })
                db.session.commit()
                return jsonify({'status': True, 'msg': '正在刷新...'})
            else:
                cate = Category()
                cate.name = cateName
                db.session.add(cate)
                db.session.commit()
                return jsonify({'status': True, 'msg': '正在刷新...'})


# 分类编辑
@app.route('/category_edit/<cateid>', methods=['POST', 'GET'])
@login_required
def category_edit(cateid):
    if current_user.role == "vistor":
        return render_template('blog/index.html')
    else:
        cateName = request.form['e-cate-name']
        # print(cateName)
        cate = Category.query.filter_by(id=cateid, is_deleted=0).first()
        if(cate.name == cateName):
            return jsonify({'status': False, 'msg': '不能与原分类名称相同！'})
        cate = Category.query.filter_by(name=cateName, is_deleted=0).first()
        if cate is not None:
            return jsonify({'status': False, 'msg': '此分类已存在！'})
        Category.query.filter_by(id=cateid).update({
            'name': cateName
        })
        db.session.commit()
        return jsonify({'status': True, 'msg': '正在刷新...'})


# 分类展示
@app.route('/category_show/<cateid>', methods=['POST', 'GET'])
@login_required
def category_show(cateid):
    if current_user.role == "vistor":
        return render_template('blog/index.html')
    else:
        cate = Category.query.filter_by(id=cateid, is_deleted=0).first()
        if cate is None:
            return jsonify({'status': False, 'msg': '此分类不存在！'})
        else:
            Category.query.filter_by(id=cateid).update({
                'is_shown': 1
            })
            db.session.commit()
            return jsonify({'status': True, 'msg': '修改成功！'})


# 分类隐藏
@app.route('/category_hide/<cateid>', methods=['POST', 'GET'])
@login_required
def category_hide(cateid):
    if current_user.role == "vistor":
        return render_template('blog/index.html')
    else:
        cate = Category.query.filter_by(id=cateid, is_deleted=0).first()
        if cate is None:
            return jsonify({'status': False, 'msg': '此分类不存在！'})
        else:
            Category.query.filter_by(id=cateid).update({
                'is_shown': 0
            })
            db.session.commit()
            return jsonify({'status': True, 'msg': '修改成功！'})


# 分类删除
@app.route('/category_del/<cateid>', methods=['POST', 'GET'])
@login_required
def category_del(cateid):
    if current_user.role == "vistor":
        return render_template('blog/index.html')
    else:
        cate = Category.query.filter_by(id=cateid, is_deleted=0).first()
        if cate is None:
            return jsonify({'status': False, 'msg': '此分类不存在！'})
        else:
            Category.query.filter_by(id=cateid).update({
                'is_deleted': 1
            })
            db.session.commit()
            return jsonify({'status': True, 'msg': '删除成功！'})


# 用户管理
@app.route('/user_manage', methods=['POST', 'GET'])
@login_required
def user_manage():
    users = User.query.filter_by(is_deleted=0).all()
    item = {'username': '', 'email': '', 'role': '', 'created': '', 'logged': '', 'tags':[]}
    userList = []
    for user in users:
        item['username'] = user.username
        item['email'] = user.email
        if user.role == 'vistor':
            item['role'] = '普通用户'
        elif user.role == 'admin':
            item['role'] = '管理员'
        item['created'] = user.created.strftime("%Y-%m-%d %H:%M:%S")
        item['logged'] = user.logged.strftime("%Y-%m-%d %H:%M:%S")
        if user.mark is None:
            item['tags'] = None
        else:
            markstrlist = user.mark.split(',')
            marklist = list(map(int, markstrlist))
            # print(marklist)
            tags = []
            for tag_id in marklist:
                tag = Tag.query.filter_by(is_deleted=0, id=tag_id).first()
                if tag is not None:
                    tags.append(copy.deepcopy(tag.name))
            item['tags'] = tags
        userList.append(copy.deepcopy(item))
        # print(json.dumps(item))
    return render_template('admin/user_manage.html', userList=userList)


# 生成标签
@app.route('/generate_tags', methods=['POST', 'GET'])
@login_required
def generate_tags():
    text = request.form['tmptext']
    text = text_filter(text)
    # print(text)
    analyse.set_stop_words('./app/static/file/stop.txt')
    tfidf = analyse.extract_tags
    kws = tfidf(text)
    tagstr = ','.join(kws[:3]);
    print(tagstr)
    return jsonify({'status': True, 'msg': 'success', 'tagstr':tagstr})


# 文章内容过滤 除去代码段
def text_filter(text):
    text = text.replace('\n', '')
    text = text.replace('\r', '')
    a1 = re.compile(r'\{.*?\}' )
    text = text.replace("<code>","{")
    text = text.replace("</code>","}")
    text = text.replace("<img ","{")
    text = text.replace(" />","}")
    text = a1.sub('',text)
    return text


# jsonTest
@app.route('/jsonTest', methods=['POST', 'GET'])
@login_required
def jsonTest():
    analyse.set_stop_words('./app/jiebatest/stop.txt')

    tfidf = analyse.extract_tags
    textrank = analyse.textrank

    with open("./app/jiebatest/doc.txt") as fileReader:
        text = fileReader.read()

    # 去除代码段
    text = text_filter(text)
    kws = tfidf(text,withWeight=True, topK=50)
    data = {'name': '', 'value': 0}
    datas = []
    for kw in kws:
        data['name'] = kw[0]
        data['value'] = int(kw[1]*1000)
        datas.append(copy.deepcopy(data))
    # print(datas)
    items = json.dumps(datas)
    return jsonify({'status': True, 'items': items})


# 生成词云数据
def get_cloud(text):
    analyse.set_stop_words('./app/jiebatest/stop.txt')
    tfidf = analyse.extract_tags
    # textrank = analyse.textrank
    # with open("./app/jiebatest/doc.txt") as fileReader:
    #     text = fileReader.read()

    # 去除代码段
    text = text_filter(text)
    kws = tfidf(text,withWeight=True, topK=50)
    data = {'name': '', 'value': 0}
    datas = []
    for kw in kws:
        data['name'] = kw[0]
        data['value'] = int(kw[1]*1000)
        datas.append(copy.deepcopy(data))
    # print(datas)
    items = json.dumps(datas)
    return items


# 获取导航栏分类
def get_categorys():
    cates = Category.query.filter_by(is_shown=1, is_deleted=0).all()
    return cates


# 全局搜索
@app.route('/search', methods=['POST', 'GET'])
def search():
    # loginForm = LoginForm()
    # registrationForm = RegistrationForm()
    cates = get_categorys()
    page = request.args.get('page', 1, type=int)

    q = request.args.get('q')

    # 需要做判断，做两种查询的兼容
    if os.environ.get('ELASTICSEARCH_URL') is not None:
        # Article.reindex()
        articles, total = Article.search(q, page, app.config['POSTS_PER_PAGE'])
    else:
        arts = Article.query.filter(or_(Article.text.ilike('%%{}%%'.format(q)), Article.title.ilike('%%{}%%'.format(q)))).filter_by(status=1, is_deleted=0).order_by(Article.created.desc()).paginate(
                page, app.config['POSTS_PER_PAGE'], False)
        articles = arts.items
        total = Article.query.filter(or_(Article.text.ilike('%%{}%%'.format(q)), Article.title.ilike('%%{}%%'.format(q)))).filter_by(status=1, is_deleted=0).count()

    articleList = get_article_list(articles)
    
    next_url = url_for('search', q=q, page=page + 1) \
        if total > page * app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('search', q=q, page=page - 1) \
        if page > 1 else None

    return render_template('blog/index.html', cates=cates, loginForm=g.loginForm, registrationForm=g.registrationForm,
                            q=q, search=1, total=total, articleList=articleList, 
                            prev_url=prev_url, next_url=next_url, blog_name=g.blog_name)


# 生成推荐标记
@app.route('/getmark', methods=['GET'])
@login_required
def getmark():
    start, end = get_se_of_recent_month()
    # print('start={}, end={}'.format(start, end))
    users = User.query.filter_by(is_deleted=0).all()
    nums = len(users)
    # print('nums={}'.format(nums))
    for user in users:
        # print('='*30)
        # print('user={}-{}'.format(user.id, user.username))
        records = Record.query.filter(Record.rtime>=start, Record.rtime<=end).filter_by(user_id=user.id, is_deleted=0).all()
        if records is None or len(records)==0:
            # print('---------1')
            nums -= 1
            continue
        # print('user={}-{}'.format(user.id, user.username))        
        tags = []        
        for record in records:
            relations = Relation.query.filter_by(art_id=record.art_id, is_deleted=0).all()
            for relation in relations:
                tag = Tag.query.filter_by(id=relation.tag_id, is_deleted=0).first()
                if tag is not None:
                    tags.append(tag)
        tag_dict = {}
        for tag in tags:
            # print('tag_id={}, name={}'.format(tag.id, tag.name))
            if tag.id in tag_dict:
                tag_dict[tag.id] += 1
            else:
                tag_dict[tag.id] = 1
        # print(tag_dict)
        max_tag_ids = []
        for i in range(3):
            max_tag_id = max(tag_dict, key=tag_dict.get)
            max_tag_ids.append(str(max_tag_id))
            tag_dict[max_tag_id] = 0
        # print(max_tag_ids)
        # print('='*30)
        if max_tag_ids is not None and len(max_tag_ids)!=0:
            markstr = ','.join(max_tag_ids)
            User.query.filter_by(id=user.id).update({
                'mark' : markstr
            })
            db.session.commit()
    return jsonify({'status': True, 'msg': '成功为{}名用户添加推荐标记，正在刷新...'.format(nums)})
    # return jsonify({'status': False, 'msg': '为用户添加推荐标记失败！'})


# 获取请求中的有关信息用于访问记录
def get_reqinfo(request):
    ip = request.remote_addr
    if ip is None:
        ip = request.headers['X-Real-IP']
    if ip is None:
        ip = request.headers['X-Forwarded-For']
    platform = request.user_agent.platform
    browser = request.user_agent.browser
    version = request.user_agent.version
    language = request.user_agent.language
    return {'ip': ip, 'platform': platform, 'browser': browser, 'version': version, 'language': language}


# 获取一周的开始和结束  type：datetime
def get_se_of_week():
    day_of_week = datetime.now().weekday()
    today =  int(time.mktime(date.today().timetuple()))
    start = datetime.fromtimestamp(today-day_of_week*86400)
    end = datetime.fromtimestamp(today+(7-day_of_week)*86400-1)
    return start, end

def get_se_of_today():
    today =  int(time.mktime(date.today().timetuple()))
    start = datetime.fromtimestamp(today)
    end = datetime.fromtimestamp(today+86399)
    return start, end

# 获取最近一周时间开始和结束  type：datetime
def get_se_of_recent_week():
    today =  int(time.mktime(date.today().timetuple()))
    start = datetime.fromtimestamp(today-6*86400)
    end = datetime.fromtimestamp(today+86399)
    return start, end


# 获取以今天23:59结束的最近30天的开始和结束 type：datetime
def get_se_of_recent_month():
    today =  int(time.mktime(date.today().timetuple()))
    start = datetime.fromtimestamp(today-29*86400)   # 30*86400 = 2592000
    end = datetime.fromtimestamp(today+86399)
    return start, end

def get_se_of_recent_season():
    today =  int(time.mktime(date.today().timetuple()))
    start = datetime.fromtimestamp(today-89*86400)  
    end = datetime.fromtimestamp(today+86399)
    return start, end



@app.route('/admin_option', methods=['POST', 'GET'])
@login_required
def admin_option():
    return render_template('admin/admin_option.html')


@app.route('/get_options', methods=['POST', 'GET'])
@login_required
def get_options():
    options = Option.query.filter_by(is_deleted=0).all()
    opt = {}
    for option in options:
        opt[option.name] = option.value
    return jsonify({'status': True, 'options': json.dumps(opt)})
        

@app.route('/opt_edit', methods=['POST', 'GET'])
@login_required
def opt_edit():
    blog_name = request.args.get('blog_name')
    if blog_name is not None:
        Option.query.filter_by(name='blog_name').update({
            'value': blog_name
        })
        db.session.commit()
        g.blog_name = blog_name
        return jsonify({'status': True, 'msg': '博客名称已保存，正在刷新...'})
    
    back_song = request.args.get('back_song')
    if back_song is not None:
        Option.query.filter_by(name='song').update({
            'value': back_song
        })
        db.session.commit()
        return jsonify({'status': True, 'msg': '音乐链接已保存，正在刷新...'})


# 最近访问
@app.route('/records', methods=['POST', 'GET'])
@login_required
def records():
    page = request.args.get('page', 1, type=int)
    reqtime = request.args.get('reqtime', 'week', type=str)
    if reqtime == 'week':
        start, end = get_se_of_recent_week()
    elif reqtime == 'today':
        start, end = get_se_of_today()
    elif reqtime == 'month':
        start, end = get_se_of_recent_month()
    elif reqtime == 'season':
        start, end = get_se_of_recent_season()
    # print('start={}'.format(start))
    # print('end={}'.format(end))
    recs = Record.query.filter(Record.rtime>=start, Record.rtime<=end).filter_by(is_deleted=0).order_by(Record.rtime.desc()).paginate(
            page, app.config['RECORDS_PER_PAGE'], False)
    next_url = url_for('records', reqtime=reqtime, page=recs.next_num) \
            if recs.has_next else None
    prev_url = url_for('records', reqtime=reqtime, page=recs.prev_num) \
            if recs.has_prev else None 
    records = recs.items

    articles = {}
    for record in records:
        article = Article.query.filter_by(id=record.art_id, is_deleted=0).first()
        if article is not None:
            articles[record.id] = article.title

    return render_template('admin/records.html', records = records, articles=articles, 
                            next_url=next_url, prev_url=prev_url, page=page, page_size=app.config['RECORDS_PER_PAGE'])


# 访问统计
@app.route('/records_statistic', methods=['POST', 'GET'])
@login_required
def records_statistic():
    get_labels_and_items()
    return render_template('admin/records_statistic.html')


def get_labels_and_items():
    labels = []
    items = []
    week_dict = {0:'周一', 1:'周二', 2:'周三', 3:'周四', 4:'周五', 5:'周六', 6:'周日'}
    start, end = get_se_of_recent_week()
    records = Record.query.filter(Record.rtime>=start, Record.rtime<=end).filter_by(is_deleted=0).all()
    rec_dict = {}
    for record in records:
        rdate = record.rtime.strftime("%Y-%m-%d")
        if rdate in rec_dict:
            rec_dict[rdate] += 1
        else:
            rec_dict[rdate] = 1
    
    date_list = sorted(rec_dict)
    for d in date_list:
        week = datetime.strptime(d, '%Y-%m-%d').weekday()
        labels.append(week_dict[week])
    labels[-1] = '今天'
    for label in labels:
        if label == '周日':
            break
        labels[labels.index(label)] = '上'+label
    for rdate in date_list:
        items.append(rec_dict[rdate])
    print(labels)
    print(items)
    return labels, items
