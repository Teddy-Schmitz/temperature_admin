import pytest
from app.factory import create_app
from app.extensions import db as _db, arduino as _arduino
from models.event import Event, EventType
from models.temperature import Temperature
from models.users import User
import tempfile
import os
import json
import arrow

TESTDB = 'autotemp_test.db'
TESTDB_PATH = '{0}/{1}'.format(tempfile.gettempdir(), TESTDB)
TESTDB_URI = 'sqlite:///{}'.format(TESTDB_PATH)


@pytest.yield_fixture(scope='session')
def app(request):
    test_config = {
        'SQLALCHEMY_DATABASE_URI': TESTDB_URI,
        'TESTING': True,
        'SCHEDULER': False,
        'ARDUINO_IP': '127.0.0.1'
    }
    test_app = create_app(test_config)
    ctx = test_app.app_context()
    ctx.push()
    yield test_app
    ctx.pop()


@pytest.yield_fixture(scope='session')
def db(app, request):
    _db.app = app
    _db.create_all()

    yield _db

    _db.drop_all()
    os.unlink(TESTDB_PATH)


@pytest.yield_fixture(scope='function')
def session(db, request):

    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options)

    db.session = session

    yield session

    transaction.rollback()
    connection.close()
    session.remove()


@pytest.yield_fixture(scope='function')
def fake_events(session, request):
    test_event, e2, e3 = Event(), Event(), Event()

    test_event.event = EventType.on
    e2.event = EventType.off
    e3.event = EventType.on
    e2.event_description = 'test description'

    test_event.timestamp = arrow.utcnow().replace(minutes=-5)
    e2.timestamp = test_event.timestamp.replace(minutes=-5)
    e3.timestamp = test_event.timestamp.replace(minutes=-10)

    session.add_all([e3, e2, test_event])
    session.commit()

    yield test_event


@pytest.yield_fixture(scope='function')
def fake_temperatures(session, request):
    test_temp, t2, t3 = Temperature(), Temperature(), Temperature()

    test_temp.temp = 25.52
    t2.temp = 26.63
    t3.temp = 27.74

    test_temp.humidity = 35.52
    t2.humidity = 36.63
    t3.humidity = 37.74

    test_temp.timestamp = arrow.utcnow().replace(minutes=-5)
    t2.timestamp = test_temp.timestamp.replace(minutes=-5)
    t3.timestamp = test_temp.timestamp.replace(minutes=-10)

    session.add_all([test_temp, t2, t3])

    session.commit()

    yield test_temp


@pytest.yield_fixture(scope='function')
def fake_users(session, request):
    u = User()
    u.username = 'test_user'
    u.password = 'test_password'
    session.add(u)
    session.commit()

    yield u


@pytest.yield_fixture(scope='function')
def test_client(app):
    client = app.test_client()
    yield client


@pytest.yield_fixture()
def arduino(request, monkeypatch, app):
    _arduino.app = app
    marker = request.node.get_marker('json_data')
    monkeypatch.setattr('app.arduino_api.Arduino._req', lambda *a: json.loads(*marker.args))
    yield _arduino
