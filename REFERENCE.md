# VL53L5CX Function Reference <!--omit in toc-->

- [VL53L5CX Function Reference](#vl53l5cx-function-reference)
  - [Basic Setup](#basic-setup)
  - [Functions](#functions)
    - [Enable Ranging & Get Data](#enable-ranging--get-data)
      - [Start Ranging](#start-ranging)
      - [Stop Ranging](#stop-ranging)
      - [Power Mode](#power-mode)
      - [Check Data Available](#check-data-available)
      - [Get Data](#get-data)
        - [Structure of Data](#structure-of-data)
        - [Reflectance](#reflectance)
        - [Target Status](#target-status)
    - [Distance](#distance)
      - [Ranging Frequency](#ranging-frequency)
      - [Resolution](#resolution)
      - [Integration Time](#integration-time)
      - [Sharpener](#sharpener)
      - [Target Order](#target-order)
    - [Motion](#motion)
      - [Enable Motion](#enable-motion)
      - [Configure Motion Distance Window](#configure-motion-distance-window)
  - [Useful Links](#useful-links)

## Basic Setup

By default the VL53L5CX library uses i2c bus 1 (/dev/i2c-1) and address 0x29.

A basic setup looks like this:

```python
import vl53l5cx

tof = vl53l5cx.vl53l5cx()

tof.start_ranging()

while True:
    if tof.data_ready():
        data = tof.get_data()
        print(data.distance_mm)
```

The sensor will be intialised automatically when the class is constructed. This involves sending > 80kb (yes, you read that right) of firmware data in order for it to function.

You can skip this initialisation by supplying the `skip_init=True` argument for a faster init on a sensor that hasn't lost power or been reset since it was last initialised:

```python
import vl53l5cx

tof = vl53l5cx.vl53l5cx(skip_init=True)
```

## Functions

### Enable Ranging & Get Data

#### Start Ranging

Start ranging should be called after configuring distance settings. Ensure you have set your desired resolution, frequency and integration time then:

```python
tof.start_ranging()
```

#### Stop Ranging

For low-power applications, or intermittent readings you can also stop ranging:

```python
tof.stop_ranging()
```

#### Power Mode

The VL53L5CX has two power modes: Continuous and Autonomous.

The operating mode can be selected with:

```python
tof.set_power_mode(mode)
```

Where `mode` is one of `vl53l5cx.POWER_MODE_SLEEP` or `vl53l5cx.POWER_MODE_WAKEUP`.

#### Check Data Available

The availability of new data is indicated by `data_ready` which returns `True` if new data is available. This should happen roughly at the frequency you've configured:

```python
if tof.data_ready():
    data = tof.get_data()
```

#### Get Data

Data is retrieved using the `get_data` method:

```python
data = tof.get_data()
```

This returns a structured element (a CTypes wrapper around the raw C struct) which, in practise, behaves like a named tuple.

##### Structure of Data

The returned data contains:

* `silicon_temp_degc` - chip temperature in degrees celsius
* `ambient_per_spad` - ambient light detected on a SPAD while no light is being emitted by the sensor.
* `nb_target_detected` - targets detected in current zone
* `nb_spads_enabled` - number of SPADs enabled for the measurement - a far or low reflectance target will activate more SPADs.
* `signal_per_spad` - quantity of photons measured during the VCSEL pulse (always on during Continuous, selective during Autonomous ranging)
* `range_sigma_mm` - estimator for the noise in the reported
target distance.
* `distance_mm` - target distance in mm
* `reflectance` - (estimated) target reflectance in %
* `target_status` - target status
* `motion_indicator` - Motion data (see below)

Most of these values (except temperature) are lists of 64 entries, one for each of the zones in the sensor.

A SPAD (single photon avalanche diode) is a single sensor element of the 8x8 VL53L5CX array.

TODO: the reference manual

##### Reflectance

The reflectance value is a percentage of emitted light returned by the target. White targets will generally have a higher reflectance, and grey/black targets will have a lower reflectance. This is useful for tracking a bright target (ping pong ball on a stick perhaps) across the array, irrespective of distance.

Note that distance and reflectance values are independent and not dependent upon each other. The *phase* of returned light pulses is used to calculate the distance, while the reflectance is simply the amount of light returned.

See the `examples/reflectance_240x240_lcd.py` example for a visualisation of reflectance on a 240x240 pixel SPI LCD.

##### Target Status

The status value indicates the validity of ranging data.

Values of `5` *or* `9` indicate that the data is ok. Although in practise only `5` implies 100% confidence in the range data.

You can convert this data to a bool like so:

```python
status = map(lambda status: status in (5, 9), data.target_status)
```

The full list of status values is as follows:

* 0 - Ranging data are not updated
* 1 - Signal rate too low on SPAD array
* 2 - Target phase
* 3 - Sigma estimator too high
* 4 - Target consistency failed
* 5 - Range valid
* 6 - Wrap around not performed (Typically the first range)
* 7 - Rate consistency failed
* 8 - Signal rate too low for the current target
* 9 - Range valid with large pulse (may be due to a merged target)
* 10 - Range valid, but no target detected at previous range
* 11 - Measurement consistency failed
* 12 - Target blurred by another one, due to sharpener
* 13 - Target detected but inconsistent data. Frequently happens for secondary targets.
* 255 - No target detected (only if number of target detected is enabled)

### Distance

#### Ranging Frequency

Ranging frequency is the rate at which new range data is calculated.

At 4x4 resolution this can be from 1-60Hz.

At 8x8 resolution this can be from 1-15Hz.

```python
tof.set_ranging_frequency_hz(15)
```

#### Resolution

Ranging resolution controls the effective resolution of output data.

In 8x8 mode the full array is used and the ranging data list will be 64 entries long, with the bottom left of the array being the first element.

In 4x4 mode the array is treated as 4x4 elements, offers a faster update rate and only outputs 16 entries.

```python
tof.set_resolution(8*8)
```

See any of the 240x240 LCD examples for a demonstration of how to convert the output data list into a 2D array (useful for feature recognition or visual representation) using numpy. In brief it looks something like this:

```python
while True:
    if vl53.data_ready():
        data = vl53.get_data()
        distance = numpy.array(data.distance_mm).reshape((8, 8)).astype('float64')
        distance = numpy.flipud(distance)
```

#### Integration Time

Integration time is the amount of time the sensor takes to perform a single reading. This cannot be greater than the ranging frequency period.

EG: a 15Hz ranging frequency cannot have more than a 66ms integration time.

```python
tof.set_ranging_frequency(15)
tof.set_integration_time_ms(66)
```

#### Sharpener

Signals returned by a target are not clean pulses with sharp edges due to "[veiling glare](https://en.wikipedia.org/wiki/Veiling_glare)". Distances reported in adjacent zones may be affected, almost like the foreground target is blurred.

The sharpener removes some of the signal caused by veiling glare, sharpeneing the foreground target and potentially revealing targets behind it. The default value is 5% and values from 0% to 99% are supported.

```python
tof.set_sharpener_percent(50)
```

#### Target Order

TODO: Right now the VL53L5CX driver only seems to support one target, enabling multiple targets results in no data.

If you want to try it, you'll need to change the `VL53L5CX_NB_TARGET_PER_ZONE` value in `setup.py` to `4` (the maximum number of targets) and also change `NB_TARGET_PER_ZONE` in `vl53l5cx_ctypes/__init__.py` before recompiling the library. (You can use `python3 setup.py develop --user` for this.)

Data for multiple targets is simply concatenated onto the end of `signal_per_spad`, `range_sigma_mm`, `distance_mm`, `reflectance` and `target_status`.

Target order controls how detected targets are sorted in the output data. They can be sorted by signal strength (`TARGET_ORDER_STRONGES`) or by distance (`TARGET_ORDER_CLOSEST`), eg:

```python
tof.set_target_order(TARGET_ORDER_STRONGEST)
```

### Motion

The VL53L5CX supports motion data output. Motion is calculated based on the change between sequential data frames, and is detected at a fixed distance window from the sensor.

Motion data is available in the `motion_indicator` property, and comprises:

* `global_indicator_1`
* `global_indicator_2`
* `status`
* `nb_of_detected_aggregates`
* `nb_of_aggregates`
* `spare`
* `motion`

TODO: I cannot determine what any of the additional fields above are for.

#### Enable Motion

Motion indication must be enabled before the data will be output:

```python
tof.enable_motion_indicator(4*4)
```

It should use the same resolution that the distance sensor is configured to use, albet in practise there are only 32 entries of motion data and only the first 16 ever seem to be populated. These make sense plotted as a 4x4 map. See `examples/motion_240x240_lcd.py` for an example.

TODO: Why is there no 8x8 motion data despite the resoution being configurable?

#### Configure Motion Distance Window

The effective motion distance can be changed, but can be no less than 400mm (40cm) from the sensor and the window no greater than 1500mm (150cm).

By default this widow is

To change it, call:

```python
tof.set_motion_distance(distance_min, distance_max)
```

The minimum and maximum distances should be given in millimeters.

## Useful Links

* Datasheet - https://www.st.com/resource/en/datasheet/vl53l5cx.pdf
* ULD driver manual - https://www.st.com/resource/en/user_manual/um2884-a-guide-to-using-the-vl53l5cx-multizone-timeofflight-ranging-sensor-with-wide-field-of-view-ultra-lite-driver-uld-stmicroelectronics.pdf