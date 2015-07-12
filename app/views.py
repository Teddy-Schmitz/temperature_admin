from flask import request, abort, jsonify, Response, render_template, Blueprint, current_app
from functools import wraps
from models.temperature import Temperature
from models.event import Event, EventType
from models.users import User
from app.factory import socketio, db, arduino
import arrow
import json

blueprint = Blueprint('frontend', __name__)


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    user = User.query.filter(User.username == username).first()

    if user:
        return user.password == password
    else:
        return False


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@blueprint.route('/')
def index():
    return render_template('index.html')


@blueprint.route('/users')
@requires_auth
def users():
    return render_template('users.html', users=db.session.query(User).all())


@socketio.on('register')
def register_connection():
    print('Registered Connection')


def send_chart_data(_, changes):
    """Send chart data when a new temperature object is committed to the database."""
    for model, change in changes:
        if isinstance(model, Temperature) and change == 'insert':
            temp_data = model
            socketio.emit('chart_data', json.dumps(temp_data.serialize))


@blueprint.route('/data', methods=['POST'])
def receive_data():
    """ Received data (temperature and humidity) from arduino
    :arg t - temperature
    :arg h - humidity
    :return:
    """
    if not request.json or not request.json.get('temperature') or not request.json.get('humidity'):
        abort(400)

    data = Temperature(temp=request.json['temperature'], humidity=request.json['humidity'])
    db.session.add(data)
    db.session.commit()
    return "Created", 201


@blueprint.route('/event', methods=['POST'])
def receive_event():
    """ Create an event.
    :arg event - EventType
    :arg description - String description of the event
    :return:
    """
    if not request.json or not request.json.get('event'):
        abort(400)
    try:
        event = Event(event=EventType[request.json['event']])
        event.event_description = request.json.get('description')
        db.session.add(event)
        db.session.commit()
    except KeyError:
        abort(400)

    return "Created", 201


@blueprint.route('/data', methods=['GET'])
def send_data():
    """ Return JSON of the last 30 minutes of temperature/humidity data
       :arg range - how many minutes to return data from. (Default 60)
    """
    range = request.args.get('range', '30')
    time = arrow.utcnow().replace(minutes=-int(range))
    data = Temperature.query\
        .filter(Temperature.timestamp > time).order_by(Temperature.timestamp.desc()).all()
    return jsonify(results=[i.serialize for i in data])


@blueprint.route('/event', methods=['GET'])
def send_event():
    """ Return JSON of the last 60 minutes of event data
       :arg range - how many minutes to return data from. (Default 60)
    """
    range = request.args.get('range', '60')
    time = arrow.utcnow().replace(minutes=-int(range))
    data = Event.query.filter(Event.timestamp > time).order_by(Event.timestamp.desc()).all()
    return jsonify(results=[i.serialize for i in data])


@blueprint.route('/event/last')
def send_last_event():
    data = Event.last_event()
    return jsonify(results=data.serialize)


@blueprint.route('/poweron')
@requires_auth
def send_power_on():
    if request.json:
        description = request.json.get('description', None) or 'website on'
    else:
        description = 'website on'
    if arduino.turn_on():
        Event.create_event(EventType.on, description)
        return 'OK', 200
    return 'Error', 500


@blueprint.route('/poweroff')
@requires_auth
def send_power_off():
    if request.json:
        description = request.json.get('description') or 'website off'
    else:
        description = 'website off'
    if arduino.turn_off():
        Event.create_event(EventType.off, description)
        return 'OK', 200
    return 'Error', 500


@blueprint.route('/users/<username>', methods=['POST'])
@requires_auth
def modify_user(username):
    u = User.query.filter(User.username == username).first_or_404()
    password = request.form.get('password', None)
    if all([u, password]):
        u.password = password
        db.session.add(u)
        db.session.commit()
        return 'OK', 200


@blueprint.route('/users/create', methods=['POST'])
@requires_auth
def create_user():
    name = request.form.get('username', None)
    password = request.form.get('password', None)
    if all([name, password]):
        u = User()
        u.password = password
        u.username = name
        db.session.add(u)
        db.session.commit()
        return 'OK', 200
    return 'Error', 400


@blueprint.route('/users/delete/<username>')
@requires_auth
def delete_user(username):
    u = User.query.filter(User.username == username).first_or_404()
    if u:
        db.session.delete(u)
        db.session.commit()
        return 'OK', 200
