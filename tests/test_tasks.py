from app.tasks import monitor_ac_usage, monitor_temperatures
from models.event import Event, EventType
from sqlalchemy_utils import naturally_equivalent
from models.temperature import Temperature
from decimal import Decimal
import pytest


@pytest.mark.json_data('{ "Good data": "asdfa"}')
def test_monitor_ac_usage_turn_off(fake_events, arduino, app):
    old_event = fake_events.timestamp
    monitor_ac_usage(1)
    new_event = Event.last_event()
    old_event = Event.query.filter(Event.timestamp == old_event).first()

    assert naturally_equivalent(old_event, new_event) is False
    assert new_event.event == EventType.off
    assert new_event.event_description == 'AutoOff Timer'


@pytest.mark.json_data('{ "Good data": "asdfa"}')
def test_monitor_ac_usage_leave_on(fake_events, arduino):
    old_event = fake_events.timestamp
    monitor_ac_usage()
    new_event = Event.last_event()
    old_event = Event.query.filter(Event.timestamp == old_event).first()

    assert naturally_equivalent(old_event, new_event)
    assert new_event.event == EventType.on
    assert new_event.event_description is None


@pytest.mark.json_data('{ "temperature": 33.42, "humidity": 46.74}')
def test_monitor_temperatures(arduino, fake_temperatures):
    old_temp = fake_temperatures.timestamp
    monitor_temperatures()
    old_temp = Temperature.query.filter(Temperature.timestamp == old_temp).first()
    new_temp = Temperature.latest_temperature()

    assert naturally_equivalent(old_temp, new_temp) is False
    assert new_temp.temp == Decimal('33.4200')
    assert new_temp.humidity == Decimal('46.7400')
