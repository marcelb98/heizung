# Configuration for heizung

class Config:
    secret_key = b'ahg76r985vndvntas869dsf6'
    database_url = 'sqlite:////home/marcel/heizung.sql'

class Hardware:
    """ Configuration for connected Hardware """
    # define GPIO-Pins of relays. {relay_nr: gpio_pin}
    relays = {
        1: 37,
        2: 35,
        3: 33,
        4: 31,
        5: 29,
        6: 36,
        7: 38,
        8: 40
    }

class System:
    """ Configuration regarding the (operating) system """

    # Direction with 1-wire devices
    # on Raspbian usually  /sys/bus/w1/devices
    dir_1w = '/home/marcel/w1/devices'