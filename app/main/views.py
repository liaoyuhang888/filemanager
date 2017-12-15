# -*- coding: utf-8 -*-
__author__ = 'lyh'
__time__ = '2017/12/15'

from app.main import main

@main.route('/', methods=['GET', 'POST'])
def index():
    return 'hello world!'