import time
import vl53l5cx

vl53 = vl53l5cx.VL53L5CX()
vl53.start_ranging()

while True:
    if vl53.data_ready():
        data = vl53.get_data()
        print("Got data!")
        print(data.distance_mm[0])
    time.sleep(0.1)
