
import time
import math
import sysconfig
import pathlib
from smbus2 import SMBus, i2c_msg
from ctypes import CDLL, CFUNCTYPE, POINTER, Structure, pointer, byref, c_int, c_uint, c_int8, c_uint8, c_int16, c_uint16, c_uint32

_I2C_CHUNK_SIZE = 2048

_I2C_RD_FUNC = CFUNCTYPE(c_int, c_uint8, c_uint16, POINTER(c_uint8), c_uint32)
_I2C_WR_FUNC = CFUNCTYPE(c_int, c_uint8, c_uint16, POINTER(c_uint8), c_uint32)
_SLEEP_FUNC = CFUNCTYPE(c_int, c_uint32)

# Path to the library dir
_PATH = pathlib.Path(__file__).parent.parent.absolute()

# System OS/Arch dependent module name suffix
_SUFFIX = sysconfig.get_config_var('EXT_SUFFIX')

# Library name
_NAME = pathlib.Path("vl53l5cx_python").with_suffix(_SUFFIX)

# Load the DLL
_VL53 = CDLL(_PATH / _NAME)


class VL53L5CX_MotionData(Structure):
    _fields_ = [
            ("global_indicator_1", c_uint32),
            ("global_indicator_2", c_uint32),
            ("status", c_uint8),
            ("nb_of_detected_aggregates", c_uint8),
            ("nb_of_aggregates", c_uint8),
            ("spare", c_uint8),
            ("motion", c_uint32 * 32)
    ]


class VL53L5CX_ResultsData(Structure):
    _fields_ = [
            ("silicon_temp_degc", c_int8),
            ("ambient_per_spad", c_uint32 * 64),
            ("nb_target_detected", c_uint8 * 64),
            ("nb_spads_enabled", c_uint32 * 64),
            ("signal_per_spad", c_uint32 * 64),
            ("range_sigma_mm", c_uint16 * 64),
            ("distance_mm", c_int16 * 64),
            ("reflectance", c_uint8 * 64),
            ("target_status", c_uint8 * 64),
            ("motion_indicator", VL53L5CX_MotionData)
    ]


class VL53L5CX:
    def __init__(self, i2c_addr=0x29):
        self._configuration = None
        self._motion_configuration = None

        def _i2c_read(address, reg, data_p, length):
            #print(f"read {address} {reg:04x} {length}")
            msg_w = i2c_msg.write(address, [reg >> 8, reg & 0xff])
            msg_r = i2c_msg.read(address, length)
            self._i2c.i2c_rdwr(msg_w, msg_r)

            for index in range(length):
                data_p[index] = ord(msg_r.buf[index])

            return 0

        def _i2c_write(address, reg, data_p, length):
            #print(f"write {address} {reg:04x} {length}")
            # Copy the ctypes pointer data into a Python list
            data = []
            for i in range(length):
                data.append(data_p[i])

            chunks = math.ceil(length / float(_I2C_CHUNK_SIZE))
            current_chunk = 1

            for offset in range(0, length, _I2C_CHUNK_SIZE):
                chunk = data[offset:offset + _I2C_CHUNK_SIZE]
                msg_w = i2c_msg.write(address, [(reg + offset) >> 8, (reg + offset) & 0xff] + chunk)
                #print(f"chunk {current_chunk} of {chunks} ({_I2C_CHUNK_SIZE} bytes)")
                self._i2c.i2c_rdwr(msg_w)

            return 0

        def _sleep(ms):
            #print(f"sleep {ms}ms")
            time.sleep(ms / 1000.0)
            return 0

        self._i2c = SMBus(1)
        self._i2c_rd_func = _I2C_RD_FUNC(_i2c_read)
        self._i2c_wr_func = _I2C_WR_FUNC(_i2c_write)
        self._sleep_func = _SLEEP_FUNC(_sleep)
        self._configuration = _VL53.get_configuration(i2c_addr, self._i2c_rd_func, self._i2c_wr_func, self._sleep_func)
        if _VL53.vl53l5cx_is_alive(self._configuration) != 0:
            raise RuntimeError(f"VL53L5CX not detected on 0x{i2c_addr:02x}")

        status = _VL53.vl53l5cx_init(self._configuration)

    def __del__(self):
        if self._configuration:
            _VL53.cleaup_configuration(self._configuration)
        if self._motion_configuration:
            _VL53.cleanup_motion_configuration(self._motion_configuration)

    def enable_motion_indicator(self, resolution=64):
        if self._motion_configuration is None:
            self._motion_configuration = _VL53.get_motion_configuration()
        return _VL53.vl53l5cx_motion_indicator_init(self._configuration, self._motion_configuration, resolution) == 0

    def set_motion_distance(self, distance_min, distance_max):
        if self._motion_configuration is None:
            raise RuntimeError("Enable motion first.")
        if distance_min < 400:
            raise ValueError("distance_min must be >= 400mm")
        if distance_max - distance_min > 1500:
            raise ValueErorr("distance between distance_min and distance_max must be < 1500mm")
        return _VL53.vl53l5cx_motion_indicator_set_distance_motion(self._configuration, self._motion_configuration, distance_min, distance_max)

    def start_ranging(self):
        _VL53.vl53l5cx_start_ranging(self._configuration)

    def stop_ranging(self):
        _VL53.vl53l5cx_stop_ranging(self._configuration)

    def set_i2c_address(self, i2c_address):
        _VL53.vl53l5cx_set_i2c_address(self._configuration, i2c_address << 1)

    def set_ranging_mode(self, ranging_mode):
        _VL53.vl53l5cx_set_ranging_mode(self._configuration, ranging_mode)

    def set_ranging_frequency_hz(self, ranging_frequency_hz):
        _VL53.vl53l5cx_set_ranging_frequency_hz(self._configuration, ranging_frequency_hz)

    def set_resolution(self, resolution):
        _VL53.vl53l5cx_set_resolution(self._configuration, resolution)

    def set_integration_time_ms(self, integration_time_ms):
        _VL53.vl53l5cx_set_integration_time_ms(self._configuration, integration_time_ms)

    def set_sharpener_percent(self, sharpener_percent):
        _VL53.vl53l5cx_set_sharpener_percent(self._configuration, sharpener_percent)

    def set_target_order(self, target_order):
        _VL53.vl53l5cx_set_target_order(self._configuration, target_order)

    def set_power_mode(self, power_mode):
        _VL53.vl53l5cx_set_power_mode(self._configuration, power_mode)

    def data_ready(self):
        ready = c_int(0)
        status = _VL53.vl53l5cx_check_data_ready(self._configuration, byref(ready))
        return ready.value and status == 0

    def get_data(self):
        results = VL53L5CX_ResultsData()
        status = _VL53.vl53l5cx_get_ranging_data(self._configuration, byref(results))
        return results

