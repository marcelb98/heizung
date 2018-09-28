heizung
=======
Installation
------------
Installing heizung on your Raspi is quite easy.
Just follow these simple steps:

1. Setup your hardware (more below)
2. Clone the repo in ``/opt`` [1]_ on your raspi, cd into this directory
3. Edit ``config.py`` to your needs (info below)
4. ``export PYTHONPATH=./``
5. ``./setup.sh``
6. Copy the systemd-files from ``./systemd`` to ``/etc/systemd/system``;
   you can delete the ``systemd`` directory now.
7. start and enable systemd:
    1. ``systemctl start heizungWebstart.service``
    2. ``systemctl enable heizungWebstart.service``
    3. ``systemctl start heizungGetSensorValues.timer``
    4. ``systemctl enable heizungGetSensorValues.timer``
    5. ``systemctl start heizungSetRelays.timer``
    6. ``systemctl enable heizungSetRelays.timer``


.. [1] You can also choose another directory, but you have to edit the systemd-services if you do so.

Config
------
You can (and should) configure heizung using the ``config.py`` file.

First of all make shure to set ``Config.secret_key`` to an random (and secret) value.

Choose a location for the database and write it to ``Config.database_url``.

You should not change the ``Hardware`` class if you use the hardware setup as described below.

Set ``System.dir_1w`` to the directory where your system puts the 1-wire devices.
On Raspbian this should be ``/sys/bus/w1/devices``.

Hardware setup
--------------
You'll need:

- Raspberry Pi
- Relay card
- DS18B20 temperature sensors
- female-female jumper wires
- some resistors and cable

*WIP*
