from models.users import User
from models.temperature import Temperature
from models.event import EventType, Event


def test_users(session):
    u = User()
    u.username = 'test_user'
    u.password = 'testpassword'

    session.add(u)
    session.commit()

    t = session.query(User).filter(User.username == 'test_user').first()

    assert t is not None
    assert u == t
    assert t.password == u.password
    assert t.api_key is None


def test_temperature(session):
    t = Temperature()
    t.humidity = 45.69
    t.temp = 19.94

    session.add(t)
    session.commit()

    b = session.query(Temperature).first()

    assert b is not None
    assert b == t
    assert b.humidity == t.humidity
    assert b.temp == t.temp


def test_event(session):
    e = Event()
    e.event = EventType.on
    e.event_description == 'test description'

    session.add(e)
    session.commit()

    t = session.query(Event).first()

    assert t is not None
    assert e == t
    assert t.event == EventType.on


def test_last_event(fake_events):

    fake_event = fake_events

    assert Event.last_event() == fake_event
    assert len(Event.query.all()) == 3
    assert Event.last_on() == fake_event


def test_latest_temperature(fake_temperatures):
    fake_temp = fake_temperatures

    assert Temperature.latest_temperature() == fake_temp
    assert len(Temperature.query.all()) == 3
