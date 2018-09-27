from functools import wraps

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_navigation import Navigation

import model
from config import Config
import forms

from lib.sensors import get_sensors, get_unused_1waddresses
from lib.relays import get_relays, get_unused_ports
from lib.rules import get_rules

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
def gen_nav():
    nav.Bar('main', [
        nav.Item('Dashboard', 'dashboard'),
        nav.Item('Sensors', 'index', items=[nav.Item(s.name, 'sensor', {'sensorID': s.id}) for s in get_sensors()]+
            [nav.Item('+ new', 'new_sensor')]
        ),
        nav.Item('Relays', 'index', items=[nav.Item(r.name, 'relay', {'relayID': r.id}) for r in get_relays()] +
            [nav.Item('+ new', 'new_relay')]
        ),
        nav.Item('Rules', 'index', items=[nav.Item(r.name, 'rule', {'ruleID': r.id}) for r in get_rules()] +
            [nav.Item('+ new', 'new_rule')]
        ),
        nav.Item('User administration', 'user_administration'),
        nav.Item('Logout', 'logout'),
    ])

# decorator for views which need navigation (this is needed to update the navigation without restarting flask)
def with_navigation(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        gen_nav()
        return func(*args, **kwargs)

    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard/')
@with_navigation
def dashboard():
    relays = get_relays()
    return render_template('dashboard.html', relays=relays)

@app.route('/sensor/<int:sensorID>/')
@with_navigation
def sensor(sensorID):
    return "sensor"

@app.route('/sensor/new', methods=['GET', 'POST'])
@with_navigation
def new_sensor():
    form = forms.NewSensorForm(request.form)
    form.address1w.choices = [(addr, addr) for addr in get_unused_1waddresses()]

    if request.method == 'POST' and form.validate():
        # form sent with correct data
        sensor = model.Sensor(form.address1w.data, form.name.data)
        model.db.session.add(sensor)
        model.db.session.commit()
        flash('Sensor created successfully.')

    return render_template('new_sensor.html', form=form)

@app.route('/relay/<int:relayID>/')
@with_navigation
def relay(relayID):
    return "relay"

@app.route('/relay/new', methods=['GET', 'POST'])
@with_navigation
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

@app.route('/rule/<int:ruleID>/')
@with_navigation
def rule(ruleID):
    rule = model.Rule.query.get(ruleID)

    return render_template('rule.html', rule=rule)

@app.route('/rule/new', methods=['GET', 'POST'])
@with_navigation
def new_rule():
    form = forms.NewRuleForm(request.form)
    form.op.choices = [(op.value, str(op)) for op in model.OPERATORS]

    if request.method == 'POST' and form.validate():
        # form sent with correct data
        form.op.data = model.OPERATORS(form.op.data)
        rule = model.Rule(form.name.data, form.op.data)
        model.db.session.add(rule)
        model.db.session.commit()
        flash('Rule created successfully.')
        return redirect(url_for('rule', ruleID=rule.id))

    return render_template('new_rule.html', form=form)

@app.route('/rule/<int:ruleID>/newSensorCondition', methods=['GET', 'POST'])
@with_navigation
def new_sensor_compare_condition(ruleID):
    rule = model.Rule.query.get(ruleID)

    form = forms.NewSensorConditionForm(request.form)
    form.sensor1.choices = [(s.id, s.name) for s in model.Sensor.query.all()]
    form.relation.choices = [(r.value, str(r)) for r in model.RELATIONS]
    form.sensor2.choices = [(s.id, s.name) for s in model.Sensor.query.all()]

    if request.method == 'POST' and form.validate():
        # form sent with correct data
        form.relation.data = model.RELATIONS(form.relation.data)
        c = model.Condition_sensorCompare(rule.id, form.sensor1.data, form.sensor2.data, form.relation.data)
        model.db.session.add(c)
        model.db.session.commit()
        flash('Condition created successfully.')
        return redirect(url_for('rule', ruleID=rule.id))

    return render_template('new_sensorCondition.html', rule=rule, form=form)

@app.route('/rule/<int:ruleID>/newValueCondition', methods=['GET', 'POST'])
@with_navigation
def new_value_compare_condition(ruleID):
    rule = model.Rule.query.get(ruleID)

    form = forms.NewValueConditionForm(request.form)
    form.sensor.choices = [(s.id, s.name) for s in model.Sensor.query.all()]
    form.relation.choices = [(r.value, str(r)) for r in model.RELATIONS]

    if request.method == 'POST' and form.validate():
        # form sent with correct data
        form.relation.data = model.RELATIONS(form.relation.data)
        c = model.Condition_valueCompare(rule.id, form.sensor.data, form.value.data, form.relation.data)
        model.db.session.add(c)
        model.db.session.commit()
        flash('Condition created successfully.')
        return redirect(url_for('rule', ruleID=rule.id))

    return render_template('new_valueCondition.html', rule=rule, form=form)

@app.route('/rule/<int:ruleID>/delete', methods=['GET', 'POST'])
def delete_rule(ruleID):
    rule = model.Rule.query.get(ruleID)
    model.db.session.delete(rule)
    model.db.session.commit()
    return redirect(url_for('index'))

@app.route('/admin/users/')
@with_navigation
def user_administration():
    return "user administration"

@app.route('/logout/')
def logout():
    return "logout"


if __name__ == '__main__':
    app.run()
