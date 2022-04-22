import time
import vl53l5cx
import numpy

vl53 = vl53l5cx.VL53L5CX()
vl53.set_resolution(8*8)
vl53.set_integration_time_ms(50)
vl53.start_ranging()

while True:
    if vl53.data_ready():
        data = vl53.get_data()
        arr = numpy.flipud(numpy.array(data.distance_mm).reshape((8, 8)))
        print(arr)
    time.sleep(0.1)
