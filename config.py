# -*- coding: utf-8 -*-
__author__ = 'lyh'
__time__ = '2017/12/15'

import os

basedir = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_TYPE = ('image', 'text', 'video')
    UPLOADED_FOLDER = os.path.join(basedir, 'uploads')
    PER_PAGE = 24
    MAX_FILE_SIZE = 1<<30
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'liaoyu_hang@qq.com'
    MAIL_PASSWORD = 'bjjqkfyrkxrpbhaa'
    PASSWORD_RESET_SALT = 'reset password'
    PASSWORD_RESET_TOKEN_EXPIRES = 60 * 60

    @staticmethod
    def init_app(app):
        pass

class DevelopConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:qq000123@localhost/filemanager?charset=utf8'

config = dict(
    development=DevelopConfig,
    default=DevelopConfig
)