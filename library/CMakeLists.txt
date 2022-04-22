cmake_minimum_required(VERSION 3.18)
project(VL53L5CX)


add_library(VL53L5CX_core SHARED
	platform.c
	src/VL53L5CX_ULD_API/src/vl53l5cx_api.c
	src/VL53L5CX_ULD_API/src/vl53l5cx_plugin_motion_indicator.c
	src/VL53L5CX_ULD_API/src/vl53l5cx_plugin_xtalk.c
	src/VL53L5CX_ULD_API/src/vl53l5cx_plugin_detection_thresholds.c
)

target_include_directories(VL53L5CX_core PUBLIC
	${CMAKE_CURRENT_LIST_DIR}
	${CMAKE_CURRENT_LIST_DIR}/src/VL53L5CX_ULD_API/inc
)

add_library(VL53L5CX_python MODULE
	vl53l5cx_module.cpp
)

target_link_options(VL53L5CX_python PRIVATE "-rdynamic")

target_link_libraries(VL53L5CX_python VL53L5CX_core)

add_library(VL53L5CX_class SHARED
	vl53l5cx.cpp
)

target_link_libraries(VL53L5CX_class VL53L5CX_core)

add_executable(test
	test.cpp
)

target_link_libraries(test VL53L5CX_class)
