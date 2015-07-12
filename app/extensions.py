from app.database import _SQLAlchemy as SQLAlchemy
db = SQLAlchemy()
from models import event, temperature, users


from app.arduino_api import Arduino
arduino = Arduino()

from flask.ext.socketio import SocketIO
socketio = SocketIO()

from flask.ext.migrate import Migrate
migrate = Migrate()
