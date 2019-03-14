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
from app import db
from datetime import datetime

# from app.models.user import User



@app.route('/')
@app.route('/index')
def index():
    loginForm = LoginForm()
    registrationForm = RegistrationForm()
    return render_template('blog/index.html', title="Index", loginForm=loginForm, registrationForm=registrationForm)

@app.route('/test')
def test():
    return render_template('test/test.html')

@app.route('/article')
def article():
    loginForm = LoginForm()
    registrationForm = RegistrationForm()
    return render_template('blog/article.html', title="Article", loginForm=loginForm, registrationForm=registrationForm)

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
    # return redirect(url_for('index'))
    return jsonify({'status': True})

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('blog/profile.html', user=user)


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

            tags = eval(request.form['tags'][1:-1])
            print(tags)
            print(type(tags))
            for tag in tags:
                print('tag={}'.format(tag))
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

            return jsonify({'status': True, 'msg': '发布成功！'})
    