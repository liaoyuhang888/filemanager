# -*- coding: utf-8 -*-
__author__ = 'lyh'
__time__ = '2017/12/15'

from flask import Blueprint

main = Blueprint('main', __name__)

from app.main import views