from app import app
from flask import render_template

@app.route('/')
@app.route('/index')
def index():
    return render_template('blog/index.html')

@app.route('/test')
def test():
    return render_template('test/test.html')

@app.route('/article')
def article():
    return render_template('blog/article.html')