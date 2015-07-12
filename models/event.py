__author__ = 'teddy'

from app.extensions import db
from sqlalchemy_utils import ArrowType, ChoiceType
import arrow
from enum import Enum


class EventType(Enum):
    """Enum for different event types"""
    off = 1
    on = 2
    hi = 3
    low = 4

EventType.off.label = 'Off'
EventType.on.label = 'On'
EventType.hi.label = 'High'
EventType.low.label = 'Low'


class Event(db.Model):
    """Defines the DB model that stores a/c events such as power on, power off, etc."""
    __tablename__ = 'events'
    timestamp = db.Column(ArrowType, primary_key=True, default=arrow.utcnow)
    event_description = db.Column(db.String(120))
    event = db.Column(ChoiceType(EventType, impl=db.Integer()), nullable=False)

    @classmethod
    def create_event(cls, event, description):
        event = Event(event=event, event_description=description)
        db.session.add(event)
        db.session.commit()
        return event

    @classmethod
    def last_event(cls):
        return Event.query.order_by(Event.timestamp.desc()).first()

    @classmethod
    def last_on(cls):
        return Event.query.filter(Event.event == EventType.on).order_by(Event.timestamp.desc()).first()

    @property
    def serialize(self):
        return {
            'timestamp': self.timestamp.timestamp,
            'event': self.event.label,
            'description': self.event_description
        }
