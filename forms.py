from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
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