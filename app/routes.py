from app import app
from flask import render_template, request, jsonify, redirect, url_for
from app.forms.login_form import LoginForm
from app.forms.registeration_form import RegistrationForm
import json
from flask_login import current_user, login_user, login_required, logout_user
from app.models.user import User
from app import db

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

@app.route('/profile')
def profile():
    return render_template('blog/profile.html')
