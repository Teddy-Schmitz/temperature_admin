from app.extensions import db
from sqlalchemy_utils import PasswordType


class User(db.Model):
    """Defines the model that holders user data for log ins."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), nullable=False)
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512']), nullable=False)
    api_key = db.Column(db.String(120))

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % self.username
