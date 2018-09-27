"""
Lib for relays
"""

from model import Relay, Rule, RelayRules
from config import Hardware

def get_relays():
    return Relay.query.all()

def get_unused_ports():
    ports = []
    for nr, gpio in Hardware.relays.items():
        if Relay.query.filter_by(port=nr).first() is None:
            ports.append(nr)
    return ports

def get_unused_rules_for_relay(relayID):
    # get all rules which are not linked with this relay

    # TODO: return only unlinked rules, actually it returns all rules

    return Rule.query.all()