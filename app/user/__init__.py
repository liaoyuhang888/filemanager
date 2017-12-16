# -*- coding: utf-8 -*-
__author__ = 'lyh'
__time__ = '2017/12/16'
from flask import Blueprint

user = Blueprint('user', __name__)

from app.user import views