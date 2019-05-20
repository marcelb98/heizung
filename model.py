import datetime
import random
import string

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

from enum import Enum, unique
from lib.hardware import get_sensor_value

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

    def __init__(self, username, password):
        self.username = username
        self.setPassword(password)

    def setPassword(self, password):
        self.passwort = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passwort, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class RemoteSensor(db.Model):
    __tablename__ = 'remotesensor'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, nullable=False)

    def __init__(self):
        # After creating this remote sensor, a new Sensor('rem-{RemoteSensor.id}', '{name}') has to be created
        self.key = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(15))

class Sensor(db.Model):
    __tablename__ = 'sensor'
    id = db.Column(db.Integer, primary_key=True)
    address1w = db.Column(db.String, nullable=False) # 1-wire-address
    name = db.Column(db.String, nullable=False)

    def __init__(self, address1w, name):
        self.address1w = address1w
        self.name = name

    @hybrid_property
    def is_remote(self):
        return self.address1w.startswith('rem-')

    @hybrid_property
    def remoteSensor(self):
        # returns object of remote sensor, if this sensor is a remote sensor, otherwise None
        if self.is_remote:
            id = self.address1w[4:]
            return RemoteSensor.query.get(id)
        else:
            return None

    @hybrid_property
    def value(self):
        if self.is_remote is True:
            # sensor is a remote sensor, get last known value from db
            value = SensorValue.query.filter_by(sensor_id=self.id).order_by(SensorValue.time.desc()).first()
            return value.value if value is not None else False
        else:
            # sensor is connected 1w-sensor
            return get_sensor_value(self.address1w)

class SensorValue(db.Model):
    __tablename__ = 'sensorValue'
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    def __init__(self, sensor, value):
        self.sensor_id = sensor.id
        self.time = datetime.datetime.now()
        self.value = value

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
        relayrules = self.relayrules
        for relayrule in relayrules:
            if Rule.query.get(relayrule.rule).fulfilled:
                return True
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
    conditions_sensorDiffCompare = db.relation("Condition_sensorDiffCompare")
    conditions_valueCompare = db.relationship("Condition_valueCompare")
    conditions_timeCompare = db.relationship("Condition_timeCompare")

    childs = db.relationship('Rule') # rules which act as condition for this rule

    relayrules = db.relationship('RelayRules')

    def __init__(self, name, operation):
        self.name = name
        self.op = operation

    @hybrid_property
    def conditions(self):
        return self.conditions_sensorCompare + self.conditions_sensorDiffCompare + self.conditions_valueCompare + self.conditions_timeCompare

    @hybrid_property
    def fulfilled(self):
        result = None
        for condition in self.conditions:
            if result is None:
                result = condition.fulfilled
            else:
                if self.op == OPERATORS.and_:
                    result = result and condition.fulfilled
                elif self.op == OPERATORS.or_:
                    result = result or condition.fulfilled
                else:
                    result = False # illegal rule
        return result

class RelayRules(db.Model):
    __tablename__ = 'relayRules'
    # Links relays with rules
    id = db.Column(db.Integer, primary_key=True)
    relay = db.Column(db.Integer, db.ForeignKey('relay.id'))
    rule = db.Column(db.Integer, db.ForeignKey('rule.id'))

    def __init__(self, relayID, ruleID):
        self.relay = relayID
        self.rule = ruleID

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

    @hybrid_property
    def fulfilled(self):
        sensor1 = Sensor.query.get(self.sensor1)
        sensor2 = Sensor.query.get(self.sensor2)
        if sensor1 is None or sensor2 is None:
            return False
        sensor1 = sensor1.value
        sensor2 = sensor2.value

        if self.relation == RELATIONS.lt:
            return sensor1 < sensor2
        elif self.relation == RELATIONS.leq:
            return sensor1 <= sensor2
        elif self.relation == RELATIONS.eq:
            return sensor1 == sensor2
        elif self.relation == RELATIONS.geq:
            return sensor1 >= sensor2
        elif self.relation == RELATIONS.gt:
            return sensor1 > sensor2
        else:
            # invalid relation
            return False

class Condition_sensorDiffCompare(db.Model):
    __tablename__ = 'condition_sensorDiffCompare'
    # condition is true, if:
    # sensor2.value - sensor1.value RELATION value is True
    id = db.Column(db.Integer, primary_key=True)
    rule = db.Column(db.Integer, db.ForeignKey('rule.id'))
    relation = db.Column(db.Enum(RELATIONS), nullable=False)
    sensor1 = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    sensor2 = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    value = db.Column(db.Float, nullable=False)

    def __init__(self, rule, sensor1, sensor2, value, relation):
        self.rule = rule
        self.sensor1 = sensor1
        self.sensor2 = sensor2
        self.value = value
        self.relation = relation

    def __str__(self):
        return '({s2} - {s1}) {op} {v}'.format(
            s1=Sensor.query.filter_by(id=self.sensor1).first().name,
            op=str(self.relation),
            s2=Sensor.query.filter_by(id=self.sensor2).first().name,
            v=str(self.value)
        )

    @hybrid_property
    def fulfilled(self):
        sensor1 = Sensor.query.get(self.sensor1)
        sensor2 = Sensor.query.get(self.sensor2)
        if sensor1 is None or sensor2 is None:
            return False
        sensor1 = sensor1.value
        sensor2 = sensor2.value
        diff = sensor2 - sensor1

        if self.relation == RELATIONS.lt:
            return diff < self.value
        elif self.relation == RELATIONS.leq:
            return diff <= self.value
        elif self.relation == RELATIONS.eq:
            return diff == self.value
        elif self.relation == RELATIONS.geq:
            return diff >= self.value
        elif self.relation == RELATIONS.gt:
            return diff > self.value
        else:
            # invalid relation
            return False

class Condition_valueCompare(db.Model):
    __tablename__ = 'condition_valueCompare'
    # condtion is true, if:
    # sensor1.value RELATION value is True
    id = db.Column(db.Integer, primary_key=True)
    rule = db.Column(db.Integer, db.ForeignKey('rule.id'))
    relation = db.Column(db.Enum(RELATIONS), nullable=False)
    sensor = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    value = db.Column(db.Float, nullable=False)

    def __init__(self, rule, sensor, value, relation):
        self.rule = rule
        self.sensor = sensor
        self.value = value
        self.relation = relation

    def __str__(self):
        return '{s1} {op} {v}'.format(
            s1=Sensor.query.filter_by(id=self.sensor).first().name,
            op=str(self.relation),
            v=str(self.value)
        )

    @hybrid_property
    def fulfilled(self):
        sensor = Sensor.query.get(self.sensor)
        if sensor is None:
            return False
        sensor = sensor.value

        if self.relation == RELATIONS.lt:
            return sensor < self.value
        elif self.relation == RELATIONS.leq:
            return sensor <= self.value
        elif self.relation == RELATIONS.eq:
            return sensor == self.value
        elif self.relation == RELATIONS.geq:
            return sensor >= self.value
        elif self.relation == RELATIONS.gt:
            return sensor > self.value
        else:
            # invalid relation
            return False

class Condition_timeCompare(db.Model):
    __tablename__ = 'condition_timeCompare'
    # condtion is true, if:
    # start_time <= current_time <= end_time
    id = db.Column(db.Integer, primary_key=True)
    rule = db.Column(db.Integer, db.ForeignKey('rule.id'))
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    def __init__(self, rule, start_time, end_time):
        self.rule = rule
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self):
        return '{t1} - {t2}'.format(
            t1=str(self.start_time),
            t2=str(self.end_time)
        )

    @hybrid_property
    def fulfilled(self):
        time = datetime.datetime.now().time()
        return self.start_time <= time <= self.end_time
