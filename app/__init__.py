from flask import Flask
from config import config
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

loginmanager = LoginManager()
loginmanager.login_view = 'main.index'
loginmanager.session_protection = 'strong'
loginmanager.login_message = ' please log in account'

db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    loginmanager.init_app(app)
    CSRFProtect(app)
    db.init_app(app)

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app