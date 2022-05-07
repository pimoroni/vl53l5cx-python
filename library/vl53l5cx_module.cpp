extern "C" {
	#include "vl53l5cx_api.h"
	#include "vl53l5cx_plugin_motion_indicator.h"

	void *__symbols__[] = {
		(void *)&vl53l5cx_is_alive,
		(void *)&vl53l5cx_init,
		(void *)&vl53l5cx_set_i2c_address,
		(void *)&vl53l5cx_get_power_mode,
		(void *)&vl53l5cx_set_power_mode,
		(void *)&vl53l5cx_start_ranging,
		(void *)&vl53l5cx_stop_ranging,
		(void *)&vl53l5cx_check_data_ready,
		(void *)&vl53l5cx_get_ranging_data,
		(void *)&vl53l5cx_get_resolution,
		(void *)&vl53l5cx_set_resolution,
		(void *)&vl53l5cx_get_ranging_frequency_hz,
		(void *)&vl53l5cx_set_ranging_frequency_hz,
		(void *)&vl53l5cx_get_integration_time_ms,
		(void *)&vl53l5cx_set_integration_time_ms,
		(void *)&vl53l5cx_get_sharpener_percent,
		(void *)&vl53l5cx_set_sharpener_percent,
		(void *)&vl53l5cx_get_target_order,
		(void *)&vl53l5cx_set_target_order,
		(void *)&vl53l5cx_get_ranging_mode,
		(void *)&vl53l5cx_set_ranging_mode,
		(void *)&vl53l5cx_dci_read_data,
		(void *)&vl53l5cx_dci_write_data,
		(void *)&vl53l5cx_dci_replace_data,
		// Motion
		(void *)&vl53l5cx_motion_indicator_init,
		(void *)&vl53l5cx_motion_indicator_set_distance_motion
	};

	VL53L5CX_Configuration* get_configuration(uint8_t i2c_addr, i2c_read_func i2c_read, i2c_write_func i2c_write, sleep_func sleep_ms) {
		VL53L5CX_Configuration *configuration = new VL53L5CX_Configuration{
			.platform = {
				.address = i2c_addr,
				.i2c_read = i2c_read,
				.i2c_write = i2c_write,
				.sleep = sleep_ms
			},
		};
		return configuration;
	}

	void cleanup_configuration(VL53L5CX_Configuration *configuration) {
		delete configuration;
	}

	VL53L5CX_Motion_Configuration* get_motion_configuration() {
		VL53L5CX_Motion_Configuration *configuration = new VL53L5CX_Motion_Configuration{

		};
		return configuration;
	}

	void cleanup_motion_configuration(VL53L5CX_Motion_Configuration *motion_configuration) {
		delete motion_configuration;
	}
}
