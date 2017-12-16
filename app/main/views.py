# -*- coding: utf-8 -*-
__author__ = 'lyh'
__time__ = '2017/12/15'

from app.main import main
from flask import render_template
from flask_login import current_user,login_required

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    print current_user
    return render_template('home.html')