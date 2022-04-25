# VL53L5CX Python

[![PyPi Package](https://img.shields.io/pypi/v/{{LIBNAME}}.svg)](https://pypi.python.org/pypi/{{LIBNAME}})
[![Python Versions](https://img.shields.io/pypi/pyversions/{{LIBNAME}}.svg)](https://pypi.python.org/pypi/{{LIBNAME}})

# Prerequisites

You must enable:

* i2c `sudo raspi-config nonint do_i2c 0`

# Installing

* Just run `pip3 install vl53l5cx`

In some cases you may need to use `sudo` or install pip with: `sudo apt install python3-pip`

Latest/development library from GitHub:

* `git clone https://github.com/pimoroni/vl53l5cx-python
* `cd vl53l5cx-python/library`
* `python3 setup.py install --user`
