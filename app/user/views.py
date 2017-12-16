# -*- coding: utf-8 -*-
__author__ = 'lyh'
__time__ = '2017/12/16'
from app.user import user
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import User
from app.user.forms import RegisterForm
from app import db
import time


@user.route('/', methods=['GET'])
@user.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        remember = True if remember else False
        user = User.query.filter_by(email=email).first()
        if not user or user.confirm_password(password):
            login_user(user,remember=remember)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password. Please try again.')
    return render_template('user/login.html')

@user.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('user.login'))

@user.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('email has already existed')
            return redirect(url_for('user.register'))
        user = User(name=form.name.data, email=form.email.data)
        user.password = form.password.data
        user.timestamp = int(time.time())
        db.session.add(user)
        db.session.commit()
        flash('Account registration success')
        return redirect(url_for('user.login'))
    return render_template('user/register.html', form=form)