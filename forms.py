from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField
from wtforms.validators import DataRequired, ValidationError

from model import Relay, Sensor

class NewSensorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message="No name given")])
    address1w = SelectField('1w-address', validators=[DataRequired(message="No address specified")])

    def validate_name(form, field):
        sensors = Sensor.query.filter_by(name=field.data).first()
        if sensors is not None:
            raise ValidationError("Name already in use.")

    def validate_address1w(form, field):
        sensors = Sensor.query.filter_by(address1w=field.data).first()
        if sensors is not None:
            raise ValidationError("Sensor is already configured.")

class NewRelayForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message="No name given")])
    port = SelectField('Port', validators=[DataRequired(message="No port specified")], coerce=int)

    def validate_name(form, field):
        relays = Relay.query.filter_by(name=field.data).first()
        if relays is not None:
            raise ValidationError("Name already in use.")

    def validate_port(form, field):
        relays = Relay.query.filter_by(port=field.data).first()
        if relays is not None:
            raise ValidationError("Port is already configured.")

class NewRuleForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message="No name given")])
    op = SelectField('Operation', validators=[DataRequired(message="No operation specified")], coerce=int)

class NewSensorConditionForm(FlaskForm):
    sensor1 = SelectField('Sensor 1', validators=[DataRequired(message="No sensor 1 specified")], coerce=int)
    relation = SelectField('Relation', validators=[DataRequired(message="No relation specified")], coerce=int)
    sensor2 = SelectField('Sensor 2', validators=[DataRequired(message="No sensor 2 specified")], coerce=int)

    # verify sensors and relation

class NewSensorDiffConditionForm(FlaskForm):
    sensor1 = SelectField('Sensor 1', validators=[DataRequired(message="No sensor 1 specified")], coerce=int)
    relation = SelectField('Relation', validators=[DataRequired(message="No relation specified")], coerce=int)
    sensor2 = SelectField('Sensor 2', validators=[DataRequired(message="No sensor 2 specified")], coerce=int)
    value = FloatField('Value', validators=[DataRequired(message="No value specified")], default=0)

    # verify sensors and relation

class NewValueConditionForm(FlaskForm):
    sensor = SelectField('Sensor', validators=[DataRequired(message="No sensor specified")], coerce=int)
    relation = SelectField('Relation', validators=[DataRequired(message="No relation specified")], coerce=int)
    value = FloatField('Value', validators=[DataRequired(message="No value specified")], default=0)

    # verify sensor and relation
