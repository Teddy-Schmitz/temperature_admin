from flask import Flask
from extensions import socketio, db, arduino, migrate
from app.views import blueprint, send_chart_data
from flask.ext.sqlalchemy import models_committed


def create_app(config=None):
    app = Flask(__name__)
    app.config['SCHEDULER'] = True
    app.config['DEBUG'] = False
    app.config['SERVER_IP'] = '127.0.0.1'
    app.config['SERVER_PORT'] = 5000
    app.config.from_object('config')
    if config is not None:
        app.config.update(config)
    register_extensions(app)
    if app.config['SCHEDULER']:
        from app.tasks import Scheduler
        scheduler = Scheduler()
        scheduler.init_app(app)
        scheduler.start()
    register_blueprints(app)
    return app


def register_extensions(app):
    socketio.init_app(app)
    db.init_app(app)
    arduino.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    app.register_blueprint(blueprint)
    models_committed.connect(send_chart_data, sender=app)
