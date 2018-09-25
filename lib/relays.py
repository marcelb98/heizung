"""
Lib for relays
"""

from model import Relay
from config import Hardware

def get_relays():
    return Relay.query.all()

def get_unused_ports():
    ports = []
    for nr, gpio in Hardware.relays.items():
        if Relay.query.filter_by(port=nr).first() is None:
            ports.append(nr)
    return ports