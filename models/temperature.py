from app.extensions import db
from sqlalchemy_utils import ArrowType
import arrow


class Temperature(db.Model):
    """ Defines the DB model that holds the temperature/humidity data.

    """
    timestamp = db.Column(ArrowType, primary_key=True, default=arrow.utcnow)
    temp = db.Column(db.DECIMAL(precision=6, scale=2), nullable=False)
    humidity = db.Column(db.DECIMAL(precision=6, scale=2), nullable=False)

    @classmethod
    def latest_temperature(cls):
        return Temperature.query.order_by(Temperature.timestamp.desc()).first()

    @property
    def serialize(self):
        return {
            'timestamp': self.timestamp.timestamp,
            'temp': str(self.temp),
            'humidity': str(self.humidity)
        }
