# -*- coding: utf-8 -*-
__author__ = 'lyh'
__time__ = '2018/1/19'

from flask_mail import Message
from flask import current_app, render_template
from app import mail

def send_email(to, subject, template, sender=None, **kwargs):
    sender = sender or ('admin', current_app.config['MAIL_USERNAME'])
    message = Message(subject=subject, recipients=[to],sender=sender)
    message.html = render_template(template + '.html', **kwargs)
    message.body = render_template(template + '.txt', **kwargs)
    mail.send(message)

