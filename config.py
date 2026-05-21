#配置文件

SECRET_KEY = 'FDJASGBNWKJRGONB;if' #越长越安全但解密也越慢

#数据库配置
#myssql所在的主机名
HOSTNAME = "127.0.0.1"
#MYSQL监听的端口号，默认3306
PORT = 3306
#连接MySQL的用户名，读者用自己设置的
USERNAME = "root"
#连接MySQL的密码，读者用自己设置的
PASSWORD = "123456"
#MySQL上创建的数据库名称
DATABASE = "stock_web"

DB_URI = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4'
SQLALCHEMY_DATABASE_URI = DB_URI


#邮箱配置
MAIL_SERVER = 'smtp.qq.com'
MAIL_USE_SSL = True
MAIL_PORT = 465
MAIL_USERNAME = '3280126546@qq.com'
MAIL_PASSWORD = 'ymssnhwhhbbxcgjj'
MAIL_DEFAULT_SENDER = '3280126546@qq.com'



