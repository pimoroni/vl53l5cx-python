# VL53L5CX CTypes Python Wrapper

[![PyPi Package](https://img.shields.io/pypi/v/vl53l5cx-ctypes.svg)](https://pypi.python.org/pypi/vl53l5cx-ctypes)
[![Python Versions](https://img.shields.io/pypi/pyversions/vl53l5cx-ctypes.svg)](https://pypi.python.org/pypi/vl53l5cx-ctypes)

CTypes wrapper for the Sitronix VL53L5CX Ultra-light Driver- C source mirror can be found at https://github.com/ST-mirror/VL53L5CX_ULD_driver/tree/lite/en

# Prerequisites

You must enable:

* i2c `sudo raspi-config nonint do_i2c 0`

If you're not using any i2c devices for which 400KHz is out of range (trackball), you might also want to increase your i2c baud rate.

VL53L5CX requires a firmware upload on startup, and it's *slow*. Add a baudrate to the i2c line in `/boot/config.txt` to speed it up:

```
dtparam=i2c_arm=on,i2c_arm_baudrate=400000
```

Note: The default baudrate is 200000 (200KHz) and a typical maximum for most devices is 400000 (400KHz), but you can also use 1000000 (1MHz) if you're just driving VL53L5CX sensors.

# Installing

* Just run `pip3 install vl53l5cx-ctypes`

In some cases you may need to use `sudo` or install pip with: `sudo apt install python3-pip`

Latest/development library from GitHub:

* `git clone https://github.com/pimoroni/vl53l5cx-python
* `cd vl53l5cx-python/library`
* `python3 setup.py install --user`
