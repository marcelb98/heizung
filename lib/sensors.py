"""
Lib for sensors
"""

import os

from model import Sensor
from config import System

def get_sensors():
    return Sensor.query.all()

def get_all_1waddresses():
    addresses = []
    for dir in next(os.walk(System.dir_1w))[1]:
        if dir != "w1_bus_master1":
            addresses.append(dir)
    return addresses

def get_unused_1waddresses():
    addresses = []
    for addr in get_all_1waddresses():
        if Sensor.query.filter_by(address1w=addr).first() is None:
            addresses.append(addr)
    return addresses