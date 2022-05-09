#!/usr/bin/env python3

import sys
import time
import argparse
import vl53l5cx_ctypes as vl53l5cx

parser = argparse.ArgumentParser(description='Change address options.')
parser.add_argument('--current', type=lambda x: int(x, 0), help='The current VL53L5CX i2c address.', default=vl53l5cx.DEFAULT_I2C_ADDRESS)
parser.add_argument('--desired', type=lambda x: int(x, 0), help='The desired VL53L5CX i2c address.', required=True)
args = parser.parse_args()

addr_current = args.current
addr_desired = args.desired


print(addr_current, addr_desired)

print(f"""change_i2c_address.py

Current address: {addr_current:02x}
Desired address: {addr_desired:02x}

""")

# Skip sensor init, since we're not actually going to *use* it right now
sensor = vl53l5cx.VL53L5CX(addr_current, skip_init=True)

if sensor.set_i2c_address(addr_desired):
    time.sleep(0.1)
    if sensor.is_alive():
        print("Success!")
        sys.exit(0)
    else:
        print("Could not detect sensor after change!")
        sys.exit(2)
else:
    print("Failed to set i2c address!")
    sys.exit(1)
