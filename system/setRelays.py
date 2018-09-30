#! python3

"""
Set relays to correct state.

"""

from flask import Flask

from config import Config, Hardware
from lib.hardware import get_sensor_value
import model

try:
    import RPi.GPIO as GPIO
except ImportError:
    from GPIOEmulator.EmulatorGUI import GPIO

app = Flask('heizung')
app.secret_key = Config.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = Config.database_url
app.app_context()
app.app_context().push()

relayON = GPIO.LOW
relayOFF = GPIO.HIGH

with app.app_context():
    model.db.init_app(app)

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for port, pin in Hardware.relays.items():
        GPIO.setup(pin, GPIO.OUT, initial=relayOFF)

def get_relay_state(relay):
    # Determine if relay should be on (True) or off (False)
    relayrules = relay.relayrules
    for relayrule in relayrules:
        if model.Rule.query.get(relayrule.rule).fulfilled:
            return True
    return False

def set_relay(relay, state):
    # Set state of relay
    gpiopin = Hardware.relays[relay.port]
    if state:
        print("Set gpio {} HIGH".format(gpiopin))
        GPIO.output(gpiopin, relayON)
    else:
        print("Set gpio {} LOW".format(gpiopin))
        GPIO.output(gpiopin, relayOFF)

if __name__ == '__main__':
    setup()
    for r in model.Relay.query.all():
        set_relay(r, get_relay_state(r))
