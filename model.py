from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

from enum import Enum, unique

db = SQLAlchemy()

@unique
class OPERATORS(Enum):
    and_ = 1
    or_ = 2

    def __str__(self):
        if self is OPERATORS.and_:
            return "and"
        elif self is OPERATORS.or_:
            return "or"

@unique
class RELATIONS(Enum):
    lt = 1  # less then
    leq = 2 # less or equal
    eq = 3  # equals
    geq = 4 # greater or equal
    gt = 5  # greater then

    def __str__(self):
        if self is RELATIONS.lt:
            return "<"
        elif self is RELATIONS.leq:
            return "<="
        elif self is RELATIONS.eq:
            return "=="
        elif self is RELATIONS.geq:
            return ">="
        elif self is RELATIONS.gt:
            return ">"

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

    def __init__(self, address1w, name):
        self.address1w = address1w
        self.name = name

class Relay(db.Model):
    __tablename__ = 'relay'
    id = db.Column(db.Integer, primary_key=True)
    port = db.Column(db.Integer, nullable=False) # No. of relay on relay-card
    name = db.Column(db.String, nullable=False)

    relayrules = db.relationship('RelayRules')

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
    parent_rule = db.Column(db.Integer, db.ForeignKey('rule.id'), nullable=True)
    name = db.Column(db.String, nullable=False)
    op = db.Column(db.Enum(OPERATORS), nullable=False)
    conditions_sensorCompare = db.relationship("Condition_sensorCompare")
    conditions_valueCompare = db.relationship("Condtion_valueCompare")

    childs = db.relationship('Rule') # rules which act as condition for this rule

    relayrules = db.relationship('RelayRules')

    def __init__(self, name, operation):
        self.name = name
        self.op = operation

    @hybrid_property
    def conditions(self):
        return self.conditions_sensorCompare + self.conditions_valueCompare

class RelayRules(db.Model):
    __tablename__ = 'relayRules'
    # Links relays with rules
    id = db.Column(db.Integer, primary_key=True)
    relay = db.Column(db.Integer, db.ForeignKey('relay.id'))
    rule = db.Column(db.Integer, db.ForeignKey('rule.id'))

class Condition_sensorCompare(db.Model):
    __tablename__ = 'condition_sensorCompare'
    # condtion is true, if:
    # sensor1.value RELATION sensor2.value is True
    id = db.Column(db.Integer, primary_key=True)
    rule = db.Column(db.Integer, db.ForeignKey('rule.id'))
    relation = db.Column(db.Enum(RELATIONS), nullable=False)
    sensor1 = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    sensor2 = db.Column(db.Integer, db.ForeignKey('sensor.id'))

    def __init__(self, rule, sensor1, sensor2, relation):
        self.rule = rule
        self.sensor1 = sensor1
        self.sensor2 = sensor2
        self.relation = relation

    def __str__(self):
        return '{s1} {op} {s2}'.format(
            s1=Sensor.query.filter_by(id=self.sensor1).first().name,
            op=str(self.relation),
            s2=Sensor.query.filter_by(id=self.sensor2).first().name
        )

class Condtion_valueCompare(db.Model):
    __tablename__ = 'condition_valueCompare'
    # condtion is true, if:
    # sensor1.value RELATION value is True
    id = db.Column(db.Integer, primary_key=True)
    rule = db.Column(db.Integer, db.ForeignKey('rule.id'))
    relation = db.Column(db.Enum(RELATIONS), nullable=False)
    sensor = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    value = db.Column(db.Float, nullable=False)
