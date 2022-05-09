
import time
import sysconfig
import pathlib
from smbus2 import SMBus, i2c_msg
from ctypes import CDLL, CFUNCTYPE, POINTER, Structure, byref, c_int, c_int8, c_uint8, c_int16, c_uint16, c_uint32


__version__ = '0.0.3'

DEFAULT_I2C_ADDRESS = 0x29

NB_TARGET_PER_ZONE = 1

RESOLUTION_4X4 = 16  # For completeness, feels nicer just to use 4*4
RESOLUTION_8X8 = 64

TARGET_ORDER_CLOSEST = 1
TARGET_ORDER_STRONGEST = 2

RANGING_MODE_CONTINUOUS = 1
RANGING_MODE_AUTONOMOUS = 3

POWER_MODE_SLEEP = 0
POWER_MODE_WAKEUP = 1

STATUS_OK = 0
STATUS_TIMEOUT = 1
STATUS_MCU_ERROR = 66
STATUS_INVALID_PARAM = 127
STATUS_ERROR = 255

STATUS_RANGE_NOT_UPDATED = 0
STATUS_RANGE_LOW_SIGNAL = 1
STATUS_RANGE_TARGET_PHASE = 2
STATUS_RANGE_SIGMA_HIGH = 3
STATUS_RANGE_TARGET_FAILED = 4
STATUS_RANGE_VALID = 5
STATUS_RANGE_NOWRAP = 6
STATUS_RANGE_RATE_FAILED = 7
STATUS_RANGE_SIGNAL_RATE_LOW = 8
STATUS_RANGE_VALID_LARGE_PULSE = 9
STATUS_RANGE_VALID_NO_TARGET = 10
STATUS_RANGE_MEASUREMENT_FAILED = 11
STATUS_RANGE_TARGET_BLURRED = 12
STATUS_RANGE_TARGET_INCONSISTENT = 13
STATUS_RANGE_NO_TARGET = 255

_I2C_CHUNK_SIZE = 2048

_I2C_RD_FUNC = CFUNCTYPE(c_int, c_uint8, c_uint16, POINTER(c_uint8), c_uint32)
_I2C_WR_FUNC = CFUNCTYPE(c_int, c_uint8, c_uint16, POINTER(c_uint8), c_uint32)
_SLEEP_FUNC = CFUNCTYPE(c_int, c_uint32)

# Path to the library dir
_PATH = pathlib.Path(__file__).parent.parent.absolute()

# System OS/Arch dependent module name suffix
_SUFFIX = sysconfig.get_config_var('EXT_SUFFIX')

# Library name
_NAME = pathlib.Path("vl53l5cx_ctypes").with_suffix(_SUFFIX)

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
        ("signal_per_spad", c_uint32 * 64 * NB_TARGET_PER_ZONE),
        ("range_sigma_mm", c_uint16 * 64 * NB_TARGET_PER_ZONE),
        ("distance_mm", c_int16 * 64 * NB_TARGET_PER_ZONE),
        ("reflectance", c_uint8 * 64 * NB_TARGET_PER_ZONE),
        ("target_status", c_uint8 * 64 * NB_TARGET_PER_ZONE),
        ("motion_indicator", VL53L5CX_MotionData)
    ]


class VL53L5CX:
    def __init__(self, i2c_addr=DEFAULT_I2C_ADDRESS, i2c_dev=None, skip_init=False):
        """Initialise VL53L5CX.

        :param i2c_addr: Sensor i2c address. (defualt: 0x29)
        :param skip_init: Skip (slow) sensor init (if it has not been power cycled).

        """
        self._configuration = None
        self._motion_configuration = None

        def _i2c_read(address, reg, data_p, length):
            msg_w = i2c_msg.write(address, [reg >> 8, reg & 0xff])
            msg_r = i2c_msg.read(address, length)
            self._i2c.i2c_rdwr(msg_w, msg_r)

            for index in range(length):
                data_p[index] = ord(msg_r.buf[index])

            return 0

        def _i2c_write(address, reg, data_p, length):
            # Copy the ctypes pointer data into a Python list
            data = []
            for i in range(length):
                data.append(data_p[i])

            for offset in range(0, length, _I2C_CHUNK_SIZE):
                chunk = data[offset:offset + _I2C_CHUNK_SIZE]
                msg_w = i2c_msg.write(address, [(reg + offset) >> 8, (reg + offset) & 0xff] + chunk)
                self._i2c.i2c_rdwr(msg_w)

            return 0

        def _sleep(ms):
            time.sleep(ms / 1000.0)
            return 0

        self._i2c = i2c_dev or SMBus(1)
        self._i2c_rd_func = _I2C_RD_FUNC(_i2c_read)
        self._i2c_wr_func = _I2C_WR_FUNC(_i2c_write)
        self._sleep_func = _SLEEP_FUNC(_sleep)
        self._configuration = _VL53.get_configuration(i2c_addr << 1, self._i2c_rd_func, self._i2c_wr_func, self._sleep_func)

        if not self.is_alive():
            raise RuntimeError(f"VL53L5CX not detected on 0x{i2c_addr:02x}")

        if not skip_init:
            if not self.init():
                raise RuntimeError("VL53L5CX init failed!")

    def init(self):
        """Initialise VL53L5CX."""
        return _VL53.vl53l5cx_init(self._configuration) == STATUS_OK

    def __del__(self):
        if self._configuration:
            _VL53.cleanup_configuration(self._configuration)
        if self._motion_configuration:
            _VL53.cleanup_motion_configuration(self._motion_configuration)

    def enable_motion_indicator(self, resolution=64):
        """Enable motion indicator.

        Switch on motion data output.

        :param resolution: Either 4*4 or 8*8 (default: 8*8)

        """
        if self._motion_configuration is None:
            self._motion_configuration = _VL53.get_motion_configuration()
        return _VL53.vl53l5cx_motion_indicator_init(self._configuration, self._motion_configuration, resolution) == 0

    def set_motion_distance(self, distance_min, distance_max):
        """Set motion indicator detection distance.

        :param distance_min: Minimum distance (mm), must be >= 400
        :param distance_max: Maximum distance (mm), distance_max - distance_min must be < 1500

        """
        if self._motion_configuration is None:
            raise RuntimeError("Enable motion first.")
        if distance_min < 400:
            raise ValueError("distance_min must be >= 400mm")
        if distance_max - distance_min > 1500:
            raise ValueError("distance between distance_min and distance_max must be < 1500mm")
        return _VL53.vl53l5cx_motion_indicator_set_distance_motion(self._configuration, self._motion_configuration, distance_min, distance_max)

    def is_alive(self):
        """Check sensor is connected.

        Attempts to read and validate device and revision IDs from the sensor.

        """
        is_alive = c_int(0)
        status = _VL53.vl53l5cx_is_alive(self._configuration, byref(is_alive))
        return status == STATUS_OK and is_alive.value == 1

    def start_ranging(self):
        """Start ranging."""
        _VL53.vl53l5cx_start_ranging(self._configuration)

    def stop_ranging(self):
        """Stop ranging."""
        _VL53.vl53l5cx_stop_ranging(self._configuration)

    def set_i2c_address(self, i2c_address):
        """Change the i2c address."""
        return _VL53.vl53l5cx_set_i2c_address(self._configuration, i2c_address << 1) == STATUS_OK

    def set_ranging_mode(self, ranging_mode):
        """Set ranging mode.

        :param ranging_mode: Either Continuous (RANGING_MODE_CONTINUOUS) or Autonomous (RANGING_MODE_AUTONOMOUS).

        """
        _VL53.vl53l5cx_set_ranging_mode(self._configuration, ranging_mode)

    def set_ranging_frequency_hz(self, ranging_frequency_hz):
        """Set ranging frequency.

        Set the frequency of ranging data output in continuous mode.

        :param ranging_frequency_hz: Frequency in hz from 1-60Hz at 4*4 and 1-15Hz at 8*8.

        """
        _VL53.vl53l5cx_set_ranging_frequency_hz(self._configuration, ranging_frequency_hz)

    def set_resolution(self, resolution):
        """Set sensor resolution.

        Set the sensor resolution for ranging.

        :param resolution: Either 4*4 or 8*8. The lower resolution supports a faster output data rate,

        """
        _VL53.vl53l5cx_set_resolution(self._configuration, resolution)

    def set_integration_time_ms(self, integration_time_ms):
        """Set sensor integration time.

        :param integration_time_ms: From 2ms to 1000ms. Must be lower than the ranging period.

        """
        _VL53.vl53l5cx_set_integration_time_ms(self._configuration, integration_time_ms)

    def set_sharpener_percent(self, sharpener_percent):
        """Set sharpener intensity.

        Sharpen the rolloff on the edges of closer targets to prevent them occluding more distant targets.

        :param sharpener_percent: From 0 (off) to 99 (full) (hardware default: 5%)

        """
        _VL53.vl53l5cx_set_sharpener_percent(self._configuration, sharpener_percent)

    def set_target_order(self, target_order):
        """Set target order.

        Strongest prefers targets with a higher return signal (reflectance) versus Closest preferring targets that are closer.

        :param target_order: Either Strongest (default, TARGET_ORDER_STRONGEST) or Closest (TARGET_ORDER_CLOSEST)

        """
        _VL53.vl53l5cx_set_target_order(self._configuration, target_order)

    def set_power_mode(self, power_mode):
        """Set power mode.

        :param power_mode: One of Sleep (POWER_MODE_SLEEP) or Wakeup (POWER_MODE_WAKEUP)

        """
        _VL53.vl53l5cx_set_power_mode(self._configuration, power_mode)

    def data_ready(self):
        """Check if data is ready."""
        ready = c_int(0)
        status = _VL53.vl53l5cx_check_data_ready(self._configuration, byref(ready))
        return ready.value and status == STATUS_OK

    def get_data(self):
        """Get data."""
        results = VL53L5CX_ResultsData()
        status = _VL53.vl53l5cx_get_ranging_data(self._configuration, byref(results))
        if status != STATUS_OK:
            raise RuntimeError("Error reading data.")
        return results
