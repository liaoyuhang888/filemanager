# -*- coding: utf-8 -*-
__author__ = 'lyh'
__time__ = '2017/12/16'

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1,64)])
    email = StringField('E-Mail Address', validators=[DataRequired(), Email(), Length(1,320)])
    password = PasswordField('Password',
                validators=[DataRequired(),Length(6, 20)])
    confirmPassword = PasswordField('Confirm Password',
                validators=[DataRequired(), EqualTo('password', message='password must be match')])

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                validators=[DataRequired(),Length(6, 20)])
    confirmPassword = PasswordField('Confirm Password',
                                    validators=[DataRequired(), EqualTo('password', message='password must be match')])
