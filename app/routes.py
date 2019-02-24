from app import app
from flask import render_template, request, jsonify
from app.forms.login_form import LoginForm
import json

# from app.models.user import User



@app.route('/')
@app.route('/index')
def index():
    loginForm = LoginForm()
    return render_template('blog/index.html', title="Index", loginForm=loginForm)

@app.route('/test')
def test():
    return render_template('test/test.html')

@app.route('/article')
def article():
    loginForm = LoginForm()
    return render_template('blog/article.html', title="Article", loginForm=loginForm)

@app.route('/login', methods=['POST', 'GET'])
def login():
    username = request.form['username']
    password = request.form['password']
    print('username={}, password={}'.format(username, password))
    if username=='yxj' and password=='123456':
        res = jsonify({'status': True, 'msg': '登录成功!'})
    else:
        res = jsonify({'status': False, 'msg': '用户名或密码不匹配！'})
    return  res

