# -*- coding: utf-8 -*-
__author__ = 'lyh'
__time__ = '2017/12/15'

import os

basedir = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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