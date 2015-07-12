__author__ = 'teddy'

from app.factory import socketio, db, create_app
from flask.ext.script import Manager
from flask.ext.migrate import MigrateCommand
from models.users import User

manager = Manager(create_app())
manager.add_command('db', MigrateCommand)


@manager.command
def runserver():
    socketio.run(manager.app, host=manager.app.config['SERVER_IP'], port=manager.app.config['SERVER_PORT'])


@MigrateCommand.command
def setup():
    db.create_all(app=manager.app)
    with manager.app.app_context():
        u = User()
        u.username = 'admin'
        u.password = 'admin123'
        db.session.add(u)
        db.session.commit()


if __name__ == '__main__':
    manager.run()
