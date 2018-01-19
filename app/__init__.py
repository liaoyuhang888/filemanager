from flask import Flask
from config import config
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from werkzeug.wsgi import SharedDataMiddleware

loginmanager = LoginManager()
loginmanager.login_view = 'user.login'
loginmanager.session_protection = 'strong'

db = SQLAlchemy()
mail = Mail()
csrf = CSRFProtect()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/uploads': app.config['UPLOADED_FOLDER']
    })

    loginmanager.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    mail.init_app(app)

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from app.user import user as user_blueprint
    app.register_blueprint(user_blueprint)
    return app