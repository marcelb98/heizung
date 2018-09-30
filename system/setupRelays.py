#! python3

"""
Setup GPIOs of relays.

"""

from config import Hardware

try:
    import RPi.GPIO as GPIO
except ImportError:
    from GPIOEmulator.EmulatorGUI import GPIO

relayON = GPIO.LOW
relayOFF = GPIO.HIGH

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for port, pin in Hardware.relays.items():
        GPIO.setup(pin, GPIO.OUT, initial=relayOFF)

if __name__ == '__main__':
    setup()
