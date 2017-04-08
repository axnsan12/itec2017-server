from marshmallow import fields, post_dump, pre_load
from marshmallow_sqlalchemy import field_for
from marshmallow.validate import Range
from init import ma
from models import User, RecordedLocation, Session
from datetime import timezone, datetime
from inflection import camelize, underscore


class CamelCaseSchema(ma.ModelSchema):

    @post_dump(pass_many=False)
    def snake_to_camel(self, data: dict):
        return dict((camelize(key, uppercase_first_letter=False), val) for key, val in data.items())

    @pre_load(pass_many=False)
    def camel_to_snake(self, data: dict):
        return dict((underscore(key), val) for key, val in data.items())


class TimestampUtc(fields.Field):
    def _serialize(self, value: datetime, attr, obj):
        if value is None:
            return None
        return value.replace(tzinfo=timezone.utc).timestamp()

    def _deserialize(self, value, attr, data):
        if value is None:
            return None
        return datetime.utcfromtimestamp(value).replace(tzinfo=timezone.utc)


class UserSchema(CamelCaseSchema):
    class Meta:
        model = User
        exclude = ['locations']


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class RecordedLocationSchema(CamelCaseSchema):
    class Meta:
        model = RecordedLocation

    when = TimestampUtc()
    lat = field_for(RecordedLocation, 'lat', validate=Range(min=-90, max=90, error='latitude out of range'))
    lng = field_for(RecordedLocation, 'lng', validate=Range(min=-180, max=180, error='longitude out of range'))

location_schema = RecordedLocationSchema()
locations_schema = RecordedLocationSchema(many=True)


class SessionSchema(CamelCaseSchema):
    class Meta:
        model = Session
        exclude = ['id']

    user = fields.Nested(user_schema)

session_schema = SessionSchema()
