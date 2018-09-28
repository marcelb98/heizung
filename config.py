# Configuration for heizung

class Config:
    secret_key = b'ahg76r985vndvntas869dsf6'
    database_url = 'sqlite:////home/marcel/heizung.sql'

class Hardware:
    """ Configuration for connected Hardware """
    # define GPIO-Pins of relays. {relay_nr: GPIO_BCM}
    relays = {
        1: 26,
        2: 19,
        3: 13,
        4: 6,
        5: 5,
        6: 16,
        7: 20,
        8: 21
    }

class System:
    """ Configuration regarding the (operating) system """

    # Direction with 1-wire devices
    # on Raspbian usually  /sys/bus/w1/devices
    dir_1w = '/home/marcel/w1/devices'
