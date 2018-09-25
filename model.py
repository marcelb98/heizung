from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

import enum

db = SQLAlchemy()

class OPERATORS(enum.Enum):
    and_ = 1
    or_ = 2

class RELATIONS(enum.Enum):
    lt = 1  # less then
    leq = 2 # less or equal
    eq = 3  # equals
    geq = 4 # greater or equal
    gt = 5  # greater then

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    passwort = db.Column(db.String)

    def setPassword(self, password):
        self.passwort = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passwort, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Sensor(db.Model):
    __tablename__ = 'sensor'
    id = db.Column(db.Integer, primary_key=True)
    address1w = db.Column(db.String, nullable=False) # 1-wire-address
    name = db.Column(db.String, nullable=False)


class Relay(db.Model):
    __tablename__ = 'relay'
    id = db.Column(db.Integer, primary_key=True)
    port = db.Column(db.Integer, nullable=False) # No. of relay on relay-card
    name = db.Column(db.String, nullable=False)
    rules = db.relationship('Rule')

    def __init__(self, port, name):
        self.port = port
        self.name = name

    @hybrid_property
    def on(self):
        # return True if relay is on, False otherwise
        return False

class Rule(db.Model):
    __tablename__ = 'rule'
    # One rule is defined by multiple conditions and an operatior.
    # If all conditions linked with the operator return True, the defined
    # relays will be switched.
    # Rules where parentRule is not None are acting as conditions.
    id = db.Column(db.Integer, primary_key=True)
    parent_relay = db.Column(db.Integer, db.ForeignKey('rule.id'), nullable=True)
    name = db.Column(db.String, nullable=False)
    op = db.Column(db.Enum(OPERATORS), nullable=False)
    relay = db.Column(db.Integer, db.ForeignKey('relay.id'))
    conditions_sensorCompare = db.relationship("Condition_sensorCompare")

    childs = db.relationship('Rule') # rules which act as condition for this rule

class Condition_sensorCompare(db.Model):
    __tablename__ = 'condition_sensorCompare'
    # condtion is true, if:
    # sensor1.value RELATION sensor2.value is True
    id = db.Column(db.Integer, primary_key=True)
    rule = db.Column(db.Integer, db.ForeignKey('rule.id'))
    relation = db.Column(db.Enum(RELATIONS), nullable=False)
    sensor1 = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    sensor2 = db.Column(db.Integer, db.ForeignKey('sensor.id'))

class Condtion_valueCompare(db.Model):
    __tablename__ = 'condition_valueCompare'
    # condtion is true, if:
    # sensor1.value RELATION value is True
    id = db.Column(db.Integer, primary_key=True)
    rule = db.Column(db.Integer, db.ForeignKey('rule.id'))
    relation = db.Column(db.Enum(RELATIONS), nullable=False)
    sensor = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    value = db.Column(db.Float, nullable=False)
