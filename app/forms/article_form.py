from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired

class ArticleForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired('标题不能为空！')])
    text = StringField('正文', validators=[DataRequired('正文不能为空！')])
    catecory = SelectField('分类', validators=[DataRequired('请选择一个分类！')])
    tag = StringField('标签', validators=[DataRequired('请至少选择或填写一个标签！')])
