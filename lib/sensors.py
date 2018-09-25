"""
Lib for sensors
"""

from model import Sensor

def get_sensors():
    return Sensor.query.all()