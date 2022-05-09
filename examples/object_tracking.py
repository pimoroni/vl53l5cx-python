#!/usr/bin/env python3

import time
import ST7789
import vl53l5cx_ctypes as vl53l5cx
from vl53l5cx_ctypes import STATUS_RANGE_VALID, STATUS_RANGE_VALID_LARGE_PULSE
import numpy
from scipy import ndimage
from PIL import Image


# Reflectance threshold (in % estimated signal return) for tracked target
R_THRESHOLD = 150

# Distance threshold (in mm) for tracked target
D_THRESHOLD = 400


display = ST7789.ST7789(
    width=240,
    height=240,
    rotation=90,
    port=0,
    cs=ST7789.BG_SPI_CS_BACK,  # Otherwise it will block the sensor!
    dc=9,
    backlight=18,
    spi_speed_hz=80 * 1000 * 1000,
    offset_left=0,
    offset_top=0
)


print("Uploading firmware, please wait...")
vl53 = vl53l5cx.VL53L5CX()
print("Done!")
vl53.set_resolution(8 * 8)


vl53.set_sharpener_percent(60)

# This is a visual demo, so prefer speed over accuracy
vl53.set_ranging_frequency_hz(15)
vl53.set_integration_time_ms(20)
vl53.start_ranging()


while True:
    if vl53.data_ready():
        data = vl53.get_data()

        status = numpy.isin(numpy.flipud(numpy.array(data.target_status).reshape((8, 8))), (STATUS_RANGE_VALID, STATUS_RANGE_VALID_LARGE_PULSE))
        reflectance = numpy.flipud(numpy.array(data.reflectance).reshape((8, 8))).astype('float64')
        distance = numpy.flipud(numpy.array(data.distance_mm).reshape((8, 8))).astype('float64')

        # Scale reflectance (a percentage) to 0 - 255
        reflectance *= (255.0 / 100.0)
        reflectance = numpy.clip(reflectance, 0, 255)

        # Clear invalid readings
        rfilt = numpy.where(status, reflectance, 0)

        # Clear out of range readings
        rfilt = numpy.where(distance < D_THRESHOLD, rfilt, 0)

        # Clear out of threshold readings
        rfilt = numpy.where(rfilt > R_THRESHOLD, rfilt, 0)

        # Get all possible distances for our target, replacing out of target values with "not a number"
        dfilt = numpy.where(rfilt > 0, distance, numpy.nan)

        # Get the mean distance to the target from our collected distance values
        mdist = numpy.nanmean(dfilt)
        y, x = ndimage.center_of_mass(rfilt)

        # Correct X/Y coordinates to center of view
        x -= 3.5
        y -= 3.5

        valid = not numpy.isnan(x) and not numpy.isnan(y)

        # Print 'em out. Wooohoo!
        if valid:
            print(f"{x:.02f}, {y:.02f}, {mdist:.02f}")

        # TODO: Angle to target can be calculated using trig?
        # the distance to target is the hypotenuse (c)
        # the offset in the data is the opposite (a)
        # the angle is angle (α)
        # The sensor FOV (63°) factors into this... somehow
        #
        # Better target rejection could use distance + feature size
        # to reject targets that are too big/small

        # Basic visualisation to confirm our numbers are sensible!
        rfilt = rfilt.astype('uint8')

        # Convert to a palette type image
        img = Image.frombytes("P", (8, 8), rfilt)
        img = img.convert("RGB")
        img = img.resize((240, 240), resample=Image.NEAREST)

        # Display the result
        display.display(img)


    time.sleep(0.01)  # Avoid polling *too* fast
