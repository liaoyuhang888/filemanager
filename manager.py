# -*- coding: utf-8 -*-
__author__ = 'lyh'
__time__ = '2017/12/15'
from app import create_app
from flask_script import Shell, Manager
from flask_migrate import Migrate, MigrateCommand
from app import db
from app.models import User

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app,db)


def make_shell_context():
    return dict(
        app=app,
        db=db,
        User=User
    )

manager.add_command('Shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
