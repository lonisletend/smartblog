from app import app
from flask import render_template, request, jsonify, redirect, url_for
from app.forms.login_form import LoginForm
from app.forms.registeration_form import RegistrationForm
import json
from flask_login import current_user, login_user, login_required, logout_user
from app.models.user import User
from app.models.category import Category
from app.models.article import Article
from app.models.tag import Tag
from app.models.relation import Relation
from app.models.comment import Comment
from app import db
from datetime import datetime
import copy

# from app.models.user import User


def is_del(obj):
    if obj.is_deleted==1:
        return True


@app.route('/')
@app.route('/index')
def index():
    loginForm = LoginForm()
    registrationForm = RegistrationForm()

    #文章分页
    page = request.args.get('page', 1, type=int)

    #分页查出所有可见(1)文章+倒序
    arts = Article.query.filter_by(status=1, is_deleted=0).order_by(Article.created.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=arts.next_num) \
        if arts.has_next else None
    prev_url = url_for('index', page=arts.prev_num) \
        if arts.has_prev else None
    articleList = []
    for art in arts.items:
        artdict = {'id':0, 'title':'', 'text':'', 'date':'', 'author':'', 'cateName':'', 'views':0, 'isTopping':0}
        artdict['id'] = art.id
        artdict['title'] = art.title
        artdict['text'] = art.text[:200]
        artdict['date'] = art.created.strftime("%Y-%m-%d")
        user = User.query.filter_by(id=art.user_id).first()
        artdict['author'] = user.username
        artdict['views'] = art.views
        cate = Category.query.filter_by(id=art.cate_id).first()
        artdict['cateName'] = cate.name
        artdict['isTopping'] = art.is_topping
        articleList.append(copy.deepcopy(artdict))

    return render_template('blog/index.html', title="Index", loginForm=loginForm, 
                            registrationForm=registrationForm, articleList=articleList,
                            prev_url=prev_url, next_url=next_url)


@app.route('/test')
def test():
    return render_template('test/test.html')


@app.route('/article/<artid>')
def article(artid):
    loginForm = LoginForm()
    registrationForm = RegistrationForm()

    #返回文章详情信息
    art = Article.query.filter_by(id=artid).first()
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
    res = Relation.query.filter_by(art_id=art.id).all()
    for re in res:
        tag = Tag.query.filter_by(id=re.tag_id).first()
        article['tagNames'].append(copy.deepcopy(tag.name))
    article['isTopping'] = art.is_topping
    
    # 阅读数+1
    Article.query.filter_by(id=artid).update({
        'views': art.views+1
    })
    db.session.commit()

    #返回评论信息
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

    return render_template('blog/article.html', title="Article", loginForm=loginForm, 
                            registrationForm=registrationForm, article=article, comments=comments)


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
    cmt.text = comment
    db.session.add(cmt)
    db.session.commit()
    return jsonify({'status': True, 'msg': '添加评论成功！'})

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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    # print(request.full_path)
    # return redirect(url_for('index'))
    return jsonify({'status': True})


@app.route('/profile/<username>')
# @login_required
def profile(username):
    loginForm = LoginForm()
    registrationForm = RegistrationForm()

    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_authenticated:
        comments = Comment.query.filter_by(user_id=user.id).all()
        auth = True
    else:
        comments = []
        auth = False
    return render_template('blog/profile.html', loginForm=loginForm, registrationForm=registrationForm,
                            user=user, comments=comments, auth=auth)


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



@app.route('/admin_index')
@login_required
def admin_index():
    if current_user.role == "admin":
        return render_template('admin/index.html')
    else:
        return redirect(url_for('index'))

@app.route('/admin_new', methods=['POST', 'GET'])
@login_required
def admin_new():
    if current_user.role == "vistor":
        return render_template('/index')
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
                print('art_id={}'.format(relation.art_id))
                relation.tag_id = tempTag.id
                print('tag_id={}'.format(relation.tag_id))
                db.session.add(relation)
                db.session.commit()

            return jsonify({'status': True, 'msg': '发布成功，点击跳转到文章详情页！', 'artid':tempArticle.id})
    

