#encoding: utf-8
import os
class Config(object):
    #设置了debug模式
    DEBUG = True

    #MYSQL
    DIALECT = 'mysql'
    DRIVER = 'pymysql'
    HOST = '127.0.0.1'
    PORT = '3306'
    # 一定要设置的三个属性
    DATABASE = ''
    USERNAME = 'root'
    PASSWORD = ''

    DB_URI = "{dl}+{dv}://{un}:{pw}@{host}:{port}/{db}?charset=utf8".format(dl=DIALECT,dv=DRIVER,un=USERNAME,pw=PASSWORD,host=HOST,port=PORT,db=DATABASE)

    SQLALCHEMY_DATABASE_URI = DB_URI
    # 'mysql+pymysql://用户名称:密码@localhost:端口/数据库名称'
    #如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。这需要额外的内存， 如果不必要的可以禁用它。
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True #调试设置为true

    #session加密钥匙,有且只有24个字符
    SECRET_KEY = '123456789012345678901234'
