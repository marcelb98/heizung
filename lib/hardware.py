"""
Lib to interact with hardware.

"""

from config import System

def get_sensor_value(w1addr):
    """
    Read temperature from DS18B20 sensor

    :param w1addr: 1-Wire address of sensor to read
    :return: Temperature in °C or False on read-error
    """
    data = ''
    with open(System.dir_1w+'/'+w1addr+'/w1_slave') as f:
        data = f.readlines()
    data = data.split("\n")

    if data[0].split(" ")[11] != 'YES':
        # read-error
        return False

    temp = data[1].split(" ")[9]
    return float(temp[2:]) / 1000