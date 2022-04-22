from setuptools import setup, Extension


extension = Extension(
        'vl53l5cx_python',
        define_macros=[],
        extra_compile_args=[],
        include_dirs=['.', 'src/VL53L5CX_ULD_API/inc'],
        libraries=[],
        library_dirs=[],
        sources=['platform.c',
                 'src/VL53L5CX_ULD_API/src/vl53l5cx_api.c',
                 'src/VL53L5CX_ULD_API/src/vl53l5cx_plugin_motion_indicator.c',
                 'src/VL53L5CX_ULD_API/src/vl53l5cx_plugin_xtalk.c',
                 'src/VL53L5CX_ULD_API/src/vl53l5cx_plugin_detection_thresholds.c',
	             'vl53l5cx_module.cpp'])


setup(
        name='VL53L5CX',
        version='0.0.1',
        description='VL53L5CX distance sensor driver',
        maintainer='Phil Howard',
        maintainer_email='phil@pimoroni.com',
        url='https://github.com/pimoroni/vl53l5cx-python',
        long_description='',
        long_description_content_type='text/markdown',
        ext_modules=[extension],
        packages=['vl53l5cx'],
        requires=['smbus2'],
        install_requires=['smbus2'])

