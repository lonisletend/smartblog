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
    return render_template('blog/article.html')

@app.route('/login', methods=['POST', 'GET'])
def login():

    print("test!!!!!!")
    # username = request.args.get('username')
    # password = request.args.get('password')
    data = request.get_data()
    print(data)
    print(type(data))
    json_data = request.get_json()
    print(json_data)
    print(type(json_data))

    
    res = jsonify({'ret': True, 'msg': '登录成功!'})
    res.status_code = 200
 
    return  res

