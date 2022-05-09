from setuptools import setup, Extension


extension = Extension(
    'vl53l5cx_ctypes',
    define_macros=[('VL53L5CX_NB_TARGET_PER_ZONE', '1')],
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


setup(ext_modules=[extension])
