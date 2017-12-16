# -*- coding: utf-8 -*-
__author__ = 'lyh'
__time__ = '2017-12-16'

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import loginmanager

@loginmanager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(320), nullable=False, unique=True)
    hash_password = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.Integer)

    def __init__(self, name, email):
        self.name = name
        self.email= email

    def __repr__(self):
        return "<User: {}>".format(self.name)

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.hash_password = generate_password_hash(password)

    def confirm_password(self, password):
        return check_password_hash(self.hash_password, password)