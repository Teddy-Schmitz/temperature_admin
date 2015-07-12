from apscheduler.schedulers.gevent import GeventScheduler
from flask import current_app as app
from models.event import Event, EventType
from models.temperature import Temperature
from app.extensions import arduino, db
import arrow
import logging

sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
logging.getLogger('apscheduler.scheduler').addHandler(sh)
logging.getLogger('apscheduler.executors.default').addHandler(sh)


class Scheduler:

    def __init__(self, app=None):
        self._scheduler = GeventScheduler()
        self.jobs_list = [monitor_ac_usage, monitor_temperatures]
        if app:
            self.init_app(app)

    def init_app(self, app):
        for job in self.jobs_list:
            self.add_jobs(app, job)

    def add_jobs(self, app, job):
        def call_func(*args, **kwargs):
            with app.app_context():
                func(*args, **kwargs)
        func = job

        self._scheduler.add_job(call_func, 'interval', minutes=func.minutes, coalesce=True)

    def start(self):
        self._scheduler.start()


def monitor_ac_usage(minutes=30):
    """ Checks how long AC has been running and shuts it off after max is reached.
    :param minutes: How many minutes to let the AC run continuously.
    :return:
    """
    with app.app_context():
        event = Event.last_event()
        if event and event.event != EventType.off:
            off_time = event.timestamp.replace(minutes=+minutes)
            now = arrow.utcnow()

            if off_time < now:
                if arduino.turn_off():
                    Event.create_event(EventType.off, "AutoOff Timer")


def monitor_temperatures():
    """ Checks arduino for current temperatures
    :return:
    """
    temp = arduino.check_temps()
    humid = arduino.check_humidity()

    result = Temperature(temp=temp, humidity=humid)
    with app.app_context():
        db.session.add(result)
        db.session.commit()

monitor_ac_usage.minutes = 30
monitor_temperatures.minutes = 5
