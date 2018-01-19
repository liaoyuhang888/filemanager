# -*- coding: utf-8 -*-
__author__ = 'lyh'
__time__ = '2017/12/16'
from app.user import user
from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.user.forms import RegisterForm, ResetPasswordForm
from app import db
from app.email import send_email
import time


@user.route('/', methods=['GET'])
@user.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        remember = True if remember else False
        user = User.query.filter_by(email=email).first()
        if user and user.confirm_password(password):
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
        user_ = User(name=form.name.data, email=form.email.data)
        user_.password = form.password.data
        user_.timestamp = int(time.time())
        db.session.add(user_)
        db.session.commit()
        flash('Account registration success')
        return redirect(url_for('user.login'))
    return render_template('user/register.html', form=form)

@user.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        user_ = User.query.filter_by(email=email).first()
        if user_:
            token = user_.generate_token(salt=current_app.config['PASSWORD_RESET_SALT'],
                                         expiration=current_app.config['PASSWORD_RESET_TOKEN_EXPIRES'])
            send_email(to=email,
                       subject='Reset Password',
                       template='user/email/reset_password',
                       user=user_,
                       token=token)
            session['status'] = '{} send success, please check email'.format(email)
        else:
            flash("email don't exist", 'error')
    return render_template('user/password.html')

@user.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    session.pop('status', None)
    user_ = User.token2user(token, salt=current_app.config['PASSWORD_RESET_SALT'])
    form = ResetPasswordForm()
    if user_ is None:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        password = request.form.get('password')
        user_.password = password
        db.session.add(user_)
        db.session.commit()
        flash('Your password has been updated.')
        return redirect(url_for('user.login'))
    return render_template('user/reset.html', token=token, email = user_.email, form=form)