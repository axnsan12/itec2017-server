import secrets

from typing import Optional

from flask import request, jsonify
from models import User, RecordedLocation, Session
from schema import locations_schema, user_schema, session_schema
from init import app, db
import auth


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error: InvalidUsage):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(KeyError)
def handle_missing_field(error: KeyError):
    return handle_invalid_usage(InvalidUsage("missing required field", payload={'field': error.args[0]}))


def check(value, message, status_code=None, payload=None, condition=lambda v: v):
    if not condition(value):
        raise InvalidUsage(message, status_code=status_code, payload=payload)


def check_not(value, message, status_code=None, payload=None, condition=lambda v: v):
    if condition(value):
        raise InvalidUsage(message, status_code=status_code, payload=payload)


@app.route('/users/<int:userid>/locations', methods=['POST'])
def save_locations(userid: int):
    data = request.get_json()
    check(data, "missing request data")

    session = Session.query.filter_by(token=data['token'], user_id=userid).first()  # type: Session
    check(session, "invalid token or inexistent user", status_code=401)
    user = session.user

    new_locations = locations_schema.load(data['locations'], session=db.session)
    check_not(new_locations.errors, "invalid payload", payload={'errors': new_locations.errors})

    user.add_locations(*new_locations.data)
    db.session.commit()
    return jsonify({'message': 'ok'})


@app.route('/auth/google', methods=['POST'])
def login_google():
    data = request.get_json()
    check(data, "missing request data")

    token = data['idToken']
    idinfo = auth.google_validate_token(token)
    check(idinfo, "invalid token", status_code=401)
    google_id = idinfo['sub']
    email = idinfo['email']
    name = idinfo['name']

    user = User.query.filter_by(google_id=google_id).first()  # type: Optional[User]
    if not user:
        user = User.query.filter_by(email=email).first()  # type: Optional[User]
        if not user:
            user = User(name, email, google_id)
            db.session.add(user)
        else:
            user.google_id = google_id

    session = Session(user, secrets.token_hex(40))
    db.session.add(session)
    db.session.commit()
    return session_schema.jsonify(session)


if __name__ == "__main__":
    app.run(host='0.0.0.0')


