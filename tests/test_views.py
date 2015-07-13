import base64
import json
from models.users import User
from models.event import Event, EventType
import pytest


def test_login_success(test_client, fake_users):
    auth_string = base64.b64encode('test_user:test_password')
    header = {'Authorization': 'Basic ' + auth_string}
    resp = test_client.get('/users', headers=header)
    assert resp.status_code == 200


def test_login_failure(test_client, fake_users):
    auth_string = base64.b64encode('test_user:fail_password')
    header = {'Authorization': 'Basic ' + auth_string}
    resp = test_client.get('/users', headers=header)
    assert resp.status_code == 401


def test_required_login_views(test_client, session):
    resp = test_client.get('/users')
    assert resp.status_code == 401

    resp = test_client.post('/users/test')
    assert resp.status_code == 401

    resp = test_client.post('/users/create')
    assert resp.status_code == 401

    resp = test_client.get('/users/delete/test')
    assert resp.status_code == 401

    resp = test_client.get('/poweron')
    assert resp.status_code == 401

    resp = test_client.get('/poweroff')
    assert resp.status_code == 401


def test_index(test_client):
    resp = test_client.get('/')

    assert resp.status_code == 200
    assert 'Temperature Admin' in resp.data


def test_receive_data_fail(test_client):
    resp = test_client.post('/data')
    assert resp.status_code == 400


def test_receive_data_success(test_client, fake_temperatures):
    resp = test_client.post('/data', content_type='application/json',
                            data=json.dumps(dict(temperature=45.4, humidity=50.0)))
    assert resp.status_code == 201
    assert resp.data == 'Created'


def test_receive_event_fail(test_client):
    resp = test_client.post('/event')
    assert resp.status_code == 400


def test_receive_event_success(test_client, fake_events):
    resp = test_client.post('/event', content_type='application/json',
                            data=json.dumps(dict(event='on', description='test')))
    assert resp.status_code == 201
    assert resp.data == 'Created'


def test_send_latest_event(test_client, fake_events):
    resp = test_client.get('/event/last')
    assert resp.status_code == 200

    data = json.loads(resp.data)
    assert data['results']['timestamp'] == fake_events.timestamp.timestamp


def test_send_events(test_client, fake_events):
    resp = test_client.get('/event?range=15')
    assert resp.status_code == 200

    data = json.loads(resp.data)
    assert len(data['results']) == 2


def test_send_data(test_client, fake_temperatures):
    resp = test_client.get('/data?range=15')
    assert resp.status_code == 200

    data = json.loads(resp.data)
    assert len(data['results']) == 2


def test_modify_user_success(test_client, fake_users):
    auth_string = base64.b64encode('test_user:test_password')
    header = {'Authorization': 'Basic ' + auth_string}
    resp = test_client.post('/users/test_user', headers=header, data=dict(password='changed_password'))
    user = User.query.filter(User.username == 'test_user').first()

    assert resp.status_code == 200
    assert user.password == 'changed_password'
    assert user.username == 'test_user'


def test_modify_user_failure(test_client, fake_users):
    auth_string = base64.b64encode('test_user:test_password')
    header = {'Authorization': 'Basic ' + auth_string}
    resp = test_client.post('/users/bad_user', headers=header, data=dict(password='changed_password'))
    user = User.query.filter(User.username == 'test_user').first()

    assert resp.status_code == 404
    assert user.password == 'test_password'
    assert user.username == 'test_user'


def test_delete_user_success(test_client, fake_users):
    auth_string = base64.b64encode('test_user:test_password')
    header = {'Authorization': 'Basic ' + auth_string}
    resp = test_client.get('/users/delete/test_user', headers=header)
    user = User.query.filter(User.username == 'test_user').first()

    assert resp.status_code == 200
    assert user is None


def test_delete_user_failure(test_client, fake_users):
    auth_string = base64.b64encode('test_user:test_password')
    header = {'Authorization': 'Basic ' + auth_string}
    resp = test_client.get('/users/delete/bad_user', headers=header)
    user = User.query.filter(User.username == 'test_user').first()

    assert resp.status_code == 404
    assert user.password == 'test_password'
    assert user.username == 'test_user'


def test_create_user_success(test_client, fake_users):
    auth_string = base64.b64encode('test_user:test_password')
    header = {'Authorization': 'Basic ' + auth_string}
    resp = test_client.post('/users/create', headers=header, data=dict(username='test_user2', password='test_password'))
    user = User.query.filter(User.username == 'test_user2').first()

    assert resp.status_code == 200
    assert user is not None
    assert user.username == 'test_user2'
    assert user.password == 'test_password'


def test_create_user_failure(test_client, fake_users):
    auth_string = base64.b64encode('test_user:test_password')
    header = {'Authorization': 'Basic ' + auth_string}
    resp = test_client.post('/users/create', headers=header, data=dict(username='test_user2'))
    user = User.query.filter(User.username == 'test_user2').first()

    assert resp.status_code == 400
    assert resp.data == 'Error'
    assert user is None


@pytest.mark.json_data('{ "return_value": 1}')
def test_power_on(test_client, fake_users, arduino):
    auth_string = base64.b64encode('test_user:test_password')
    header = {'Authorization': 'Basic ' + auth_string}
    resp = test_client.get('/poweron', headers=header)
    event = Event.last_event()

    assert resp.status_code == 200
    assert event.event == EventType.on


@pytest.mark.json_data('{ "return_value": 1}')
def test_power_off(test_client, fake_users, arduino):
    auth_string = base64.b64encode('test_user:test_password')
    header = {'Authorization': 'Basic ' + auth_string}
    resp = test_client.get('/poweroff', headers=header)
    event = Event.last_event()

    assert resp.status_code == 200
    assert event.event == EventType.off


@pytest.mark.json_data('{ "return_value": 0}')
def test_power_on_failure(test_client, fake_users, arduino):
    auth_string = base64.b64encode('test_user:test_password')
    header = {'Authorization': 'Basic ' + auth_string}
    resp = test_client.get('/poweron', headers=header)
    event = Event.last_event()

    assert resp.status_code == 500
    assert event is None


@pytest.mark.json_data('{ "return_value": 0}')
def test_power_off_failure(test_client, fake_users, arduino):
    auth_string = base64.b64encode('test_user:test_password')
    header = {'Authorization': 'Basic ' + auth_string}
    resp = test_client.get('/poweroff', headers=header)
    event = Event.last_event()

    assert resp.status_code == 500
    assert event is None
