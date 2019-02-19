from app import app
from flask import render_template
from app.forms.login_form import LoginForm
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

