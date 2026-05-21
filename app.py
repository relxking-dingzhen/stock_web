from flask import Flask, session, g
import config
from exts import db,mail
from models import UserModel
from blueprints.content import bp as content_bp
from blueprints.stocker import bp as stocker_bp
from flask_migrate import Migrate

app = Flask(__name__)
#绑定配置文件
app.config.from_object(config)

db.init_app(app)
mail.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(content_bp)
app.register_blueprint(stocker_bp)

#blueprint：用来做模块化

#钩子函数（hook）：before_request/ before_first_request/ after_request
#钩子函数就是插入进一个进程然后先执行钩子函数再继续运行
@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    if user_id:
        user = UserModel.query.get(user_id)
        setattr(g, 'user', user) #定义一个全局变量命名为user,值为user
    else:
        setattr(g, 'user', None)


#定义一个上下文处理器
@app.context_processor
def my_context_processor():
    return {'user': g.user}


if __name__ == '__main__':
    app.run(debug=True)