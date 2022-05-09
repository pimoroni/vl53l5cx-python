# Visual Examples

These aren't practical applications for the VL53L5CX but provide a great way to visualise what the sensor is "seeing."

They require matplotlib and numpy, install with:

```
sudo apt install python3-matplotlib python3-numpy
```

## distance_240x240_lcd.py

Basic visualisation of the 8x8 distance field.

## motion_240x240_lcd.py

Basic visualisation of 4x4 motion detection at 40cm to 1.4m

## reflectance_240x240_lcd.py

Basic visualisation of sensor estimated reflectance.

# Advanced Examples

Practical examples of the sensor as you might use it to drive a robot.

## object_tracking.py

A basic object tracking example which uses threshold based rejection to filter a single, bright target.

Uses scipy to find the target center of mass so that a robot could - potentially - follow a suitable target by turning to center it in the sensor view.

# Other Examples

## change_i2c_address.py

Simple script to change the i2c address of a sensor.

The i2c address is *not* persistent, you will need to change it again if the sensor loses power.

For multiple sensors, wire the "LP" pin on the sensor breakout to a GPIO on your Pi and pull it *LOW* to disable i2c comms on your sensor.

Bring each sensor up by releasing "LP" and setting its address in turn.

Alternatively you may want to use an i2c multiplexer - https://shop.pimoroni.com/products/tca9548a-i2c-multiplexer

Usage:

```
./change_i2c_address.py --current 0x29 --desired <desired>
```
