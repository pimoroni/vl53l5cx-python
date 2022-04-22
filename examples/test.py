import time
import vl53l5cx
import numpy

vl53 = vl53l5cx.VL53L5CX()
vl53.set_resolution(8 * 8)
vl53.enable_motion_indicator(8 * 8)
#vl53.set_integration_time_ms(50)
vl53.start_ranging()

while True:
    if vl53.data_ready():
        data = vl53.get_data()
        # TODO motion not working?
        motion = list(data.motion_indicator.motion)
        # 2d array of distance
        distance = numpy.flipud(numpy.array(data.distance_mm).reshape((8, 8)))
        # 2d array of reflectance
        reflectance = numpy.flipud(numpy.array(data.reflectance).reshape((8 , 8)))
        # 2d array of good ranging data
        status = numpy.isin(numpy.flipud(numpy.array(data.target_status).reshape((8, 8))), (5, 9))
        print(reflectance)
    time.sleep(0.1)
