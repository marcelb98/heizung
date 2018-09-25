from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, ValidationError

from model import Relay

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