import os
from datetime import timedelta


class Development:
    DEBUG = True
    ENV = 'development'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/campus-notify'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '9a3567ad426f1a8112a8b9f20a4'
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ''
    RQ_QUEUES = ['campus_notify_default']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=10)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=20)
    REDIS_URL = 'redis://localhost:6379/0'
    OTP_EXPIRES = timedelta(hours=1)
    TEXT_NAME = 'CmpNotify'
    # PAGINATE_PAGE_SIZE = 10


class Production(Development):
    DEBUG = False
    JWT_COOKIE_SECURE = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=2)
