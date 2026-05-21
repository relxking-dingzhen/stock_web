import wtforms
from wtforms.validators import Email, Length, EqualTo, DataRequired
from models import UserModel, EmailCaptchaModel
from exts import db


#注册表单验证
class RegisterForm(wtforms.Form):
    email = wtforms.StringField(validators=[Email(message='邮箱格式错误')])
    captcha = wtforms.StringField(validators=[Length(min=4, max=4, message='验证码与邮箱不匹配')])
    username = wtforms.StringField(validators=[Length(min=1, max=20, message='用户名格式错误，用户名最多20个字符')])
    password = wtforms.StringField(validators=[Length(min=6, max=18, message='密码格式错误')])
    password_confirm = wtforms.StringField(validators=[EqualTo('password', message='两次密码不一致')])

    #自定义验证
    #1.验证邮箱是否已被注册
    def validate_email(self, field):
        email = field.data
        user = UserModel.query.filter_by(email=email).first()
        if user:
            raise wtforms.ValidationError(message='该邮箱已被注册')

    #2.验证码是否正确
    def validate_captcha(self, field):
        captcha = field.data
        email = self.email.data
        captcha_model = EmailCaptchaModel.query.filter_by(email=email, captcha=captcha).first()
        if not captcha_model:
            raise wtforms.ValidationError(message='邮箱与验证码不匹配')
        else:
            db.session.delete(captcha_model)
            db.session.commit()

#登录表单验证
class LoginForm(wtforms.Form):
    email = wtforms.StringField(validators=[Email(message='邮箱格式错误')])
    password = wtforms.StringField(validators=[Length(min=6, max=18, message='密码错误')])


#文章表单验证
class ArticleForm(wtforms.Form):
    section = wtforms.SelectField(
        '版块',
        choices=[
            ('stock_focus', '股市焦点'),
            ('stock_community', '股吧'),
            ('financial_news', '财经新闻')
        ],
        validators=[DataRequired(message='请选择版块')]
    )
    title = wtforms.StringField(
        validators=[
            DataRequired(message='标题不能为空'),
            Length(min=1, max=50, message='标题长度必须在1-50字之间')
        ]
    )
    content = wtforms.TextAreaField(
        validators=[
            DataRequired(message='内容不能为空'),
            Length(min=1, max=10000, message='内容长度必须在1-10000字之间')
        ]
    )