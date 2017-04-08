from datetime import datetime

from marshmallow import ValidationError
from sqlalchemy.orm import validates

from init import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    google_id = db.Column(db.String(100), default=None)
    locations = db.relationship('RecordedLocation', backref='user', lazy='dynamic')

    def __init__(self, name=None, email=None, google_id=None):
        self.name = name
        self.email = email
        self.google_id = google_id

    def add_locations(self, *locations: 'RecordedLocation'):
        for location in locations:
            location.user = self

    def __repr__(self):
        return '<User %r>' % self.name


class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(80), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User')

    def __init__(self, user: User, token: str):
        self.user = user
        self.token = token


class RecordedLocation(db.Model):
    __tablename__ = 'recorded_locations'
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float(precision=3, scale=6))
    lng = db.Column(db.Float(precision=3, scale=6))
    when = db.Column(db.DateTime(timezone=False))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @validates('lat', 'lng')
    def validate_coordinates(self, key, value):
        if key == 'lat' and not -90 <= value <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if key == 'lng' and not -180 <= value <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees")
        return value

    def __init__(self, lat: float, lng: float, when: datetime):
        self.lat = lat
        self.lng = lng
        self.when = when


db.create_all()
