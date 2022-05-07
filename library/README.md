# VL53L5CX Python

[![PyPi Package](https://img.shields.io/pypi/v/pimoroni-vl53l5cx.svg)](https://pypi.python.org/pypi/pimoroni-vl53l5cx)
[![Python Versions](https://img.shields.io/pypi/pyversions/pimoroni-vl53l5cx.svg)](https://pypi.python.org/pypi/pimoroni-vl53l5cx)

# Prerequisites

You must enable:

* i2c `sudo raspi-config nonint do_i2c 0`

# Installing

* Just run `pip3 install pimoroni-vl53l5cx`

In some cases you may need to use `sudo` or install pip with: `sudo apt install python3-pip`

Latest/development library from GitHub:

* `git clone https://github.com/pimoroni/vl53l5cx-python
* `cd vl53l5cx-python/library`
* `python3 setup.py install --user`

# Changelog

0.0.2
-----

* Fix segfault bug in is_alive

0.0.1
-----

* Initial Release
