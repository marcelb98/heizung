#! python3

"""
Used to read the current values of all sensors and store them.

"""

from flask import Flask

from config import Config
import model

app = Flask('heizung')
app.secret_key = Config.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = Config.database_url
app.app_context()
app.app_context().push()

with app.app_context():
    model.db.init_app(app)

def get_value(w1_address):
    return 5

if __name__ == '__main__':
    for s in model.Sensor.query.all():
        v = get_value(s.address1w)
        if v:
            sv = model.SensorValue(s, v)
            model.db.session.add(sv)
    model.db.session.commit()
