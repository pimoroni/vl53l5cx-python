#include <iostream>
#include <chrono>
#include <thread>
#include <cmath>

#include <fcntl.h>

#include "vl53l5cx.hpp"
#include <linux/i2c-dev.h>

#define I2C_MSG_FMT char
#ifndef I2C_FUNC_I2C
#include <linux/i2c.h>
#define I2C_MSG_FMT __u8
#endif

#include <sys/ioctl.h>

int i2c_fd = 0;
const char *i2c_device = "/dev/i2c-1";

int i2c_read(uint8_t address, uint16_t reg, uint8_t *list, uint32_t length) {
    if(!i2c_fd){
	std::cout << "Opening " << i2c_device << std::endl;
        i2c_fd = open(i2c_device, O_RDWR);
    }

    int result;
    char cmd[2] = {(char)(reg >> 8), (char)(reg & 0xff)};

    struct i2c_msg i2c_messages[2];
    struct i2c_rdwr_ioctl_data i2c_messageset[1];

    // Send register pointer
    i2c_messages[0].addr = address;
    i2c_messages[0].flags = 0;
    i2c_messages[0].len = sizeof(cmd);
    i2c_messages[0].buf = (I2C_MSG_FMT*)cmd;

    // Read-back data
    i2c_messages[1].addr = address;
    i2c_messages[1].flags = I2C_M_RD | I2C_M_NOSTART;
    i2c_messages[1].len = length;
    i2c_messages[1].buf = (I2C_MSG_FMT*)list;

    i2c_messageset[0].msgs = i2c_messages;
    i2c_messageset[0].nmsgs = 2;

    if (ioctl(i2c_fd, I2C_RDWR, &i2c_messageset) < 0) {
	std::cout << "I2C Error: reading " << length << " bytes!"  << std::endl;
        return -1;
    }

    return 0;
}

int i2c_write(uint8_t address, uint16_t reg, uint8_t *list, uint32_t length) {
    if(!i2c_fd){
	std::cout << "Opening " << i2c_device << std::endl;
        i2c_fd = open(i2c_device, O_RDWR);
    }

    std::cout << "Writing " << length << " bytes..." << std::endl;
    /*if (length > 8192) {
	    std::cout << "Discarding chonky write of " << length << " bytes!" << std::endl;
	    return 0;
    }*/

    int result;
    uint8_t *p_list = list;

    static const int chunk_size = 2048;
    static char i2c_buf[2 + chunk_size];

    int chunks = std::ceil(length / float(chunk_size));
    int last_chunk = length % chunk_size;
    if (last_chunk == 0) {
	last_chunk = chunk_size;
    }

    struct i2c_msg i2c_messages[1];
    struct i2c_rdwr_ioctl_data i2c_messageset[1];

    /*i2c_messages[1].addr = address;
    i2c_messages[1].flags = I2C_M_NOSTART;
    i2c_messages[1].len = length;
    i2c_messages[1].buf = (I2C_MSG_FMT*)list;*/


    unsigned int offset = 0;
    for (auto i = 1u; i < chunks + 1; i++) {
	i2c_buf[0] = (char)((reg + offset) >> 8);
	i2c_buf[1] = (char)((reg + offset) & 0xff);

	// Figure out the next chunk size
	int message_size = (i == chunks) ? last_chunk : chunk_size;

	// Copy the next chunk into the buffer
	memcpy(&i2c_buf[2], &list[offset], message_size);

        // Send chunk
        i2c_messages[0].addr = address;
        i2c_messages[0].flags = 0;
        i2c_messages[0].len = 2  + message_size;
        i2c_messages[0].buf = (I2C_MSG_FMT*)i2c_buf;

	std::cout << "Sending chunk " << i << " of " << chunks << " " << message_size << " bytes" << std::endl;
	/*
	// Multi-part i2c messages with repeated starts do not work
    	i2c_messages[1].addr = address;
    	i2c_messages[1].flags = I2C_M_NOSTART | I2C_M_STOP;
    	i2c_messages[1].len = message_size;
    	i2c_messages[1].buf = (I2C_MSG_FMT*)(&list[offset]);
	*/
	offset += chunk_size;

    	i2c_messageset[0].msgs = i2c_messages;
  	i2c_messageset[0].nmsgs = 1;

        if (ioctl(i2c_fd, I2C_RDWR, &i2c_messageset) < 0) {
	    std::cout << "I2C Error: writing " << message_size << " bytes: chunk " << i << " of " << chunks << "!" << std::endl;
            return -1;
        }

    }

    return 0;
}

int sleep(uint32_t time_ms) {
	std::this_thread::sleep_for(std::chrono::milliseconds(time_ms));
	return 0;
}


using namespace pimoroni;

VL53L5CX sensor(i2c_read, i2c_write, sleep);

int main(int argc, char **argv) {
	std::cout << "Init..." << std::endl;
	sensor.init();
	std::cout << "OK" << std::endl;
	sensor.start_ranging();
	while(1){
		if(sensor.data_ready()) {
			VL53L5CX::ResultsData result;
			sensor.get_data(&result);
			std::cout << "Distance: " << result.distance_mm[0] << "mm" << std::endl;
		}
	}
}
