from flask import Flask, render_template, redirect, url_for, request, flash
from flask_navigation import Navigation

import model
from config import Config
import forms

from lib.sensors import get_sensors
from lib.relays import get_relays, get_unused_ports

def create_app():
    app = Flask('heizung')
    app.secret_key = Config.secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.database_url
    app.app_context()
    return app

app = create_app()
app.app_context().push()

with app.app_context():
    model.db.init_app(app)

nav = Navigation(app)
nav.Bar('main', [
    nav.Item('Dashboard', 'dashboard'),
    nav.Item('Sensors', 'index', items=[nav.Item(s.name, 'sensor', {'sensorID': s.id}) for s in get_sensors()]+
        [nav.Item('anlegen', 'new_sensor')]
    ),
    nav.Item('Relays', 'index', items=[nav.Item(r.name, 'relay', {'relayID': r.id}) for r in get_relays()] +
        [nav.Item('anlegen', 'new_relay')]
    ),
    nav.Item('User administration', 'user_administration'),
    nav.Item('Logout', 'logout'),
])

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard/')
def dashboard():
    relays = get_relays()
    return render_template('dashboard.html', relays=relays)

@app.route('/sensor/<int:sensorID>/')
def sensor(sensorID):
    return "sensor"

@app.route('/sensor/new')
def new_sensor():
    return "new sensor"

@app.route('/relay/<int:relayID>/')
def relay(relayID):
    return "relay"

@app.route('/relay/new', methods=['GET', 'POST'])
def new_relay():
    form = forms.NewRelayForm(request.form)
    form.port.choices = [(nr, 'Port {}'.format(nr)) for nr in get_unused_ports()]

    if request.method == 'POST' and form.validate():
        # form sent with correct data
        relay = model.Relay(form.port.data, form.name.data)
        model.db.session.add(relay)
        model.db.session.commit()
        flash('Relay created successfully.')

    return render_template('new_relay.html', form=form)

@app.route('/admin/users/')
def user_administration():
    return "user administration"

@app.route('/logout/')
def logout():
    return "logout"

@app.route('/init/')
def init():
    model.db.create_all()
    return "a"


if __name__ == '__main__':
    app.run()
