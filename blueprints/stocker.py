from flask import Blueprint, render_template, jsonify, redirect, url_for, session, g
from exts import mail, db
from flask_mail import Message
from flask import request
import string
import random
from models import EmailCaptchaModel, UserModel, ArticleModel
from .forms import RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText


#此蓝图下网站前缀均以/stocker开头
bp = Blueprint('stocker', __name__, url_prefix='/stocker')


#登陆页面
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            user = UserModel.query.filter_by(email=email).first()
            if not user:
                email_error = '邮箱未被注册'
                print(email_error)
                return render_template('login.html', email_error = email_error)
            if check_password_hash(user.password, password):
                #用cooike可以使用户处于登陆状态
                #cooike中不适合存储太多的数据，只适合存储少量的数据
                ##cooike一般用来存放登录授权的东西
                session['user_id'] = user.id #运行session意味着登陆成功
                return redirect(url_for('content.home'))
            else:
                password_error = '密码错误'
                print(password_error)
                return render_template('login.html', password_error = password_error)
        else:
            print(form.errors)
            return redirect(url_for('stocker.login'))


#GET:从服务器上获取数据
#POST:将客户端的数据提交给服务器
#注册页面
@bp.route('/register', methods=['GET', 'POST'])
def register():
    #验证用户提交的邮箱和验证码是否对应且正确
    #表单验证：flask-wtf
    if request.method == 'GET':
        return render_template('register.html')
    else:
        form = RegisterForm(request.form)
        if form.validate():
            email = form.email.data
            username = form.username.data
            password = form.password.data
            user = UserModel(email=email, username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            # 设置session，使用户直接处于登录状态
            session['user_id'] = user.id
            return redirect(url_for('content.home'))  # 改为重定向到首页
        else:
            print(form.errors)
            email_error = ''.join(form.email.errors)
            captcha_error = ''.join(form.captcha.errors)
            username_error = ''.join(form.username.errors)
            password_error = ''.join(form.password.errors)
            password_confirm_error = ''.join(form.password_confirm.errors)
            return render_template('register.html', email_error = email_error, captcha_error = captcha_error, username_error = username_error, password_error = password_error, password_confirm_error = password_confirm_error)

#获取邮箱验证码
@bp.route('/captcha/email')
def get_email_captcha():
    email = request.args.get('email')
    captcha = random.randint(1000, 9999)

    sender_email = "3280126546@qq.com"
    sender_password = "ymssnhwhhbbxcgjj"
    subject = "股票网验证码"
    body = f"你的验证码是: {captcha}（请妥善保管）"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = email

    # 创建 SMTP 会话
    server = smtplib.SMTP('smtp.qq.com', 587)  # 根据邮箱提供商修改
    server.starttls()
    server.login(sender_email, sender_password)

    # 发送邮件
    server.sendmail(sender_email, email, msg.as_string())
    server.quit()

    email_captcha = EmailCaptchaModel(email=email, captcha=captcha)
    db.session.add(email_captcha)
    db.session.commit()

    return jsonify({'code': 200, 'message': '', 'data': None})
'''
#获取邮箱验证码
@bp.route('/captcha/email')
def get_email_captcha():
    #要想导入参数有两种方法
    #方法一：/captcha/email/<email>  在路径中传参
    #方法二：/capatch/email？email=xxx@qq.com
    #以下是第二种方式
    email = request.args.get('email')
    #生成四位随机数
    
    source = string.digits*4
    captcha = random.sample(source, 4)
    captcha = ''.join(captcha)
    
    captcha = random.randint(1000, 9999)
    message = Message('YOUR CAPTCHA', recipients=[email], body=f'Your captcha is{captcha}')
    mail.send(message)
    #memcachaed/redis可以将数据放到缓存当中
    # 用数据库表的方式存储（大网站不推荐）
    email_captcha = EmailCaptchaModel(email=email, captcha=captcha)
    db.session.add(email_captcha)
    db.session.commit()
    return jsonify({'code': 200, 'message': '', 'data': None})
'''

#退出登录
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('content.home'))

#管理文章
@bp.route('/manage_article')
def manage_article():
    if not g.user:
        return redirect(url_for('stocker.login'))
    
    section = request.args.get('section', 'stock_focus')  # 默认显示股市焦点板块
    articles = ArticleModel.query.filter_by(
        author_id=g.user.id,
        section=section
    ).order_by(ArticleModel.create_time.desc()).all()
    
    return render_template('manage_article.html', articles = articles, current_section = section)