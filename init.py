from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask('route-my-way')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'

db = SQLAlchemy(app)
ma = Marshmallow(app)
