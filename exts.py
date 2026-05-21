#扩展文件
#此文件的作用是解决循环引用的问题
from flask_sqlalchemy import SQLAlchemy
from flask_mail import  Mail

db = SQLAlchemy()
mail = Mail()
