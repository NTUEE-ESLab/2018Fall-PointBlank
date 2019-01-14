#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include "mpu.h"


/*******
 *  mpu open / close fd
 */
int mpu_open() {
	int fd;

	/* I2C connect */
	printf("I2C: Connecting\n");
	if ((fd = open("/dev/i2c-1", O_RDWR)) < 0) {
		fprintf(stderr, "I2C: Failed to access %s\n", "/dev/i2c-1");
		return -1;
	}
	printf("I2C: acquiring buss to 0x%x\n", MPU_ADDRESS);
	if (ioctl(fd, I2C_SLAVE, MPU_ADDRESS) < 0) {
		fprintf(stderr, "I2C: Failed to acquire bus access/talk to slave 0x%x\n", MPU_ADDRESS);
		return -2;
	}
	return fd;
}

int mpu_close(int fd) {
	close(fd);
	return 0;
}

/*******
 *  mpu read / write register(s)
 */
int mpu_read_reg(int fd, uint8_t reg, uint8_t *val) {
	write(fd, &reg, 1);
	read(fd, val, 1);
	return 0;
}

int mpu_write_reg(int fd, uint8_t reg, uint8_t val) {
	uint8_t tmp[2] = {reg, val};
	printf("write: 0x%x, 0x%x\n", tmp[0], tmp[1]);
	if (write(fd, &tmp[0], 2) != 2) {
		fprintf(stderr, "failed to write reg(0x%x)\n", reg);
	}
	else {
		//printf("success\n");
	}
	return 0;
}

int mpu_read_chunk(int fd, uint8_t reg, uint8_t *buf, size_t size) {
	ssize_t count;

	write(fd, &reg, 1);
	count = read(fd, buf, size);
	if (count < 0) {
		perror("error\n");
		return 1;
	}
	else if (count == 0) {
		printf("eof");
		return 1;
	}
	else if (count < 6) {
		printf("incomplete data\n");
		return 1;
	}
	return 0;
}

int mpu_write_chunk(int fd, uint8_t reg, uint8_t *buf, size_t size) {
	uint8_t *tmp = (uint8_t*)malloc(size + 1);

	tmp[0] = reg;
	memcpy(tmp + 1, buf, size);
	write(fd, tmp, size + 1);
	free(tmp);

	return 0;
}

/*******
 *  mpu config
 */
int mpu_config_gyro_fs(int fd, uint8_t fullscale) {
	uint8_t val;
	uint8_t mask = 0x18; // [4:3]

	mpu_read_reg(fd, MPU_REG_GYRO_CONFIG, &val);
	val = (val & (~mask)) | (fullscale << 3);
	mpu_write_reg(fd, MPU_REG_GYRO_CONFIG, val);
	return 0;
}

int mpu_config_gyro_dlpf(int fd, uint8_t dlpf) {
	uint8_t val;
	uint8_t mask;

	if (dlpf == MPU_GYRO_DLPF_DEF0 || dlpf == MPU_GYRO_DLPF_DEF1) {
		mask = 0x03;
		mpu_read_reg(fd, MPU_REG_GYRO_CONFIG, &val);
		val = (val & ~mask) | (~dlpf);
		mpu_write_reg(fd, MPU_REG_GYRO_CONFIG, val);
	}
	else {
		/* enable extra DLPF */
		mask = 0x03;
		mpu_read_reg(fd, MPU_REG_GYRO_CONFIG, &val);
		val = val | mask;
		mpu_write_reg(fd, MPU_REG_GYRO_CONFIG, val);

		/* select extra DLPF */
		mask = 0x07;
		mpu_read_reg(fd, MPU_REG_CONFIG, &val);
		val = (val & (~mask)) | dlpf;
		mpu_write_reg(fd, MPU_REG_CONFIG, val);
	}
	return 0;
}

int mpu_config_accel_fs(int fd, uint8_t fullscale) {
	uint8_t val;
	uint8_t mask = 0x18; // [4:3]

	mpu_read_reg(fd, MPU_REG_ACCEL_CONFIG, &val);
	val = (val & (~mask)) | (fullscale << 3);
	mpu_write_reg(fd, MPU_REG_ACCEL_CONFIG, val);
	return 0;
}

int mpu_config_accel_dlpf(int fd, uint8_t dlpf) {
	uint8_t val;
	uint8_t mask;

	if (dlpf == MPU_ACCEL_DLPF_DEF) {
		mask = 0x0F;
		mpu_read_reg(fd, MPU_REG_ACCEL_CONFIG_2, &val);
		val = (val & ~mask) | (~dlpf);
		mpu_write_reg(fd, MPU_REG_ACCEL_CONFIG_2, val);
	}
	else {
		mask = 0x0F;
		mpu_read_reg(fd, MPU_REG_ACCEL_CONFIG_2, &val);
		val = (val & (~mask)) | 0x08 | dlpf;             // 0x08: enable extra DLPF
		mpu_write_reg(fd, MPU_REG_ACCEL_CONFIG_2, val);
	}
	return 0;
}

int mpu_config_bypass(int fd, uint8_t enable) {
	uint8_t val;
	mpu_read_reg(fd, MPU_INT_PIN_CFG, &val);
	val = (val & (~2)) | (enable << 1);
	mpu_write_reg(fd, MPU_INT_PIN_CFG, val);

	mpu_read_reg(fd, MPU_INT_PIN_CFG, &val);
	printf("MPU_INT_PIN_CFG: 0x%x\n", val);

	return 0;
}

int mpu_config_compass(int fd, uint8_t mode) {
	if (ioctl(fd, I2C_SLAVE, AKM_ADDRESS) < 0) {
		fprintf(stderr, "I2C: Failed to acquire bus access/talk to slave 0x%x\n", AKM_ADDRESS);
		return -2;
	}
	mpu_write_reg(fd, AKM_REG_CONTROL_2, 1);
	mode |= (1 << 4);
	mpu_write_reg(fd, AKM_REG_CONTROL_1, mode);

	if (ioctl(fd, I2C_SLAVE, MPU_ADDRESS) < 0) {
		fprintf(stderr, "I2C: Failed to acquire bus access/talk to slave 0x%x\n", MPU_ADDRESS);
		return -2;
	}
	return 0;
}


/*******
 *  mpu high-level config
 */
int mpu_config_reset(int fd) {
	uint8_t val;
	uint8_t mask;

	/* reset config in mpu */
	mpu_write_reg(fd, MPU_REG_PWR_MGMT_1, 0x80);

	/* reset fifo in mpu */
	mask = 0x04; // for sleep, cycle, and standby
	mpu_read_reg(fd, MPU_USER_CTRL, &val);
	val = (val & (~mask)) | 0x04;  // reset fifo
	//val = val & (~0x40);           // disable fifo
	mpu_write_reg(fd, MPU_USER_CTRL, val);

	/* reset and turn off compass */
	//mpu_config_bypass(fd, 1);
	//mpu_config_compass(fd, AKM_MODE_POWER_DOWN);
	mpu_config_bypass(fd, 0);
	return 0;
}

int mpu_config_sleep(int fd) {
	uint8_t val;
	uint8_t mask;

	mask = 0x70; // for sleep, cycle, and standby
	mpu_read_reg(fd, MPU_REG_PWR_MGMT_1, &val);
	val = val & (~mask);
	mpu_write_reg(fd, MPU_REG_PWR_MGMT_1, val);

	mask = 0x3F; // for accel, gyro enable
	mpu_read_reg(fd, MPU_REG_PWR_MGMT_2, &val);
	val = (val & (~mask)) | 0x3F;
	mpu_write_reg(fd, MPU_REG_PWR_MGMT_2, val);  // disable gyro and accel

	/* enable sleep mode */
	mask = 0x70; // for sleep, cycle, and standby
	mpu_read_reg(fd, MPU_REG_PWR_MGMT_1, &val);
	val = (val & (~mask)) | 0x40;
	mpu_write_reg(fd, MPU_REG_PWR_MGMT_1, val);
	return 0;
}

int mpu_config_low_power(int fd, uint8_t wom_thr, uint8_t mpu_lposc_clk) {
	uint8_t val;
	uint8_t mask;

	/* ensure accel is running */
	mask = 0x70; // for disable sleep, cycle, and standby
	mpu_read_reg(fd, MPU_REG_PWR_MGMT_1, &val);
	val = val & (~mask);
	mpu_write_reg(fd, MPU_REG_PWR_MGMT_1, val);

	mask = 0x3F; // for accel, gyro enable
	mpu_read_reg(fd, MPU_REG_PWR_MGMT_2, &val);
	val = (val & (~mask)) | 0x07;
	mpu_write_reg(fd, MPU_REG_PWR_MGMT_2, val);  // disable gyro only

	mpu_read_reg(fd, MPU_REG_PWR_MGMT_1, &val);
	//printf("MPU_REG_PWR_MGMT_1: 0x%x\n", val);
	mpu_read_reg(fd, MPU_REG_PWR_MGMT_2, &val);
	//printf("MPU_REG_PWR_MGMT_2: 0x%x\n", val);

	/* set accel LPF */
	mpu_config_accel_dlpf(fd, MPU_ACCEL_DLPF_184);

	mpu_read_reg(fd, MPU_REG_ACCEL_CONFIG_2, &val);
	//printf("MPU_REG_ACCEL_CONFIG_2: 0x%x\n", val);

	/* config interrupt properties *//*
	mask = 0xF0; // for interrupt properties
	mpu_read_reg(fd, MPU_INT_PIN_CFG, &val);
	val = (val & (~mask)) | 0x20;
	mpu_write_reg(fd, MPU_INT_PIN_CFG, val);  // enable interrupt pin and status holding

	mpu_read_reg(fd, MPU_INT_PIN_CFG, &val);
	printf("MPU_INT_PIN_CFG: 0x%x\n", val);*/

	/* enable motion interrupt *//*
	mpu_write_reg(fd, MPU_INT_ENABLE, 0x41);

	mpu_read_reg(fd, MPU_INT_ENABLE, &val);
	printf("MPU_INT_ENABLE: 0x%x\n", val);*/

	/* enable accel hardware intelligence *//*
	mask = 0xC0; // for accel, gyro enable
	mpu_read_reg(fd, MPU_MOT_DETECT_CTRL, &val);
	val = (val & (~mask)) | 0xC0;
	mpu_write_reg(fd, MPU_MOT_DETECT_CTRL, val);  // ACCEL_INTEL_EN = 1 and ACCEL_INTEL_MODE = 1

	mpu_read_reg(fd, MPU_MOT_DETECT_CTRL, &val);
	printf("MPU_MOT_DETECT_CTRL: 0x%x\n", val);*/

	/* set motion threshold */
	mpu_write_reg(fd, MPU_WOM_THR, wom_thr);

	mpu_read_reg(fd, MPU_WOM_THR, &val);
	//printf("MPU_WOM_THR: 0x%x\n", val);

	/* set freq of wake-up */
	mpu_write_reg(fd, MPU_LP_ACCEL_ODR, mpu_lposc_clk);

	mpu_read_reg(fd, MPU_LP_ACCEL_ODR, &val);
	//printf("MPU_LP_ACCEL_ODR: 0x%x\n", val);

	/* enable cycle mode */
	mask = 0x70; // for disable sleep, cycle, and standby
	mpu_read_reg(fd, MPU_REG_PWR_MGMT_1, &val);
	val = (val & (~mask)) | 0x20;
	mpu_write_reg(fd, MPU_REG_PWR_MGMT_1, val);

	mpu_read_reg(fd, MPU_REG_PWR_MGMT_1, &val);
	//printf("MPU_REG_PWR_MGMT_1: 0x%x\n", val);
	return 0;
}

int mpu_config_full_power(int fd, uint8_t gyro_fs, uint8_t gyro_dlpf, uint8_t accel_fs, uint8_t accel_dlpf) {
	uint8_t val;
	uint8_t mask;

	/* enable gyro and accel */
	mask = 0x70; // for disable sleep, cycle, and standby
	mpu_read_reg(fd, MPU_REG_PWR_MGMT_1, &val);
	val = val & (~mask);
	mpu_write_reg(fd, MPU_REG_PWR_MGMT_1, val);
	mpu_write_reg(fd, MPU_REG_PWR_MGMT_2, 0x00);

	mpu_config_gyro_fs   (fd, gyro_fs);
	mpu_config_gyro_dlpf (fd, gyro_dlpf);
	mpu_config_accel_fs  (fd, accel_fs);
	mpu_config_accel_dlpf(fd, accel_dlpf);

	return 0;
}


/*******
 *  mpu read maesurement data
 */
int mpu_read_gyro(int fd, int16_t *data) {
	uint8_t buf[6];

	mpu_read_chunk(fd, MPU_REG_GYRO, buf, 6);
	data[0] =  (int16_t)((buf[0] << 8) | buf[1]); 
	data[1] =  (int16_t)((buf[2] << 8) | buf[3]);
	data[2] =  (int16_t)((buf[4] << 8) | buf[5]);
	//printf("gyro: (%d, %d, %d)\n", data[0], data[1], data[2]);
	return 0;
}

int mpu_read_accel (int fd, int16_t *data) {
	uint8_t buf[6];

	mpu_read_chunk(fd, MPU_REG_ACCEL, buf, 6);
	data[0] = -(int16_t)((buf[0] << 8) | buf[1]);  // axes is at opposite direction.
	data[1] = -(int16_t)((buf[2] << 8) | buf[3]);  
	data[2] = -(int16_t)((buf[4] << 8) | buf[5]);
	//printf("accel: (%d, %d, %d)\n", data[0], data[1], data[2]);
	return 0;
}

int mpu_read_compass(int fd, int16_t *data) {
	uint8_t buf[6], val = 0;

	if (ioctl(fd, I2C_SLAVE, AKM_ADDRESS) < 0) {
		fprintf(stderr, "I2C: Failed to acquire bus access/talk to slave 0x%x\n", AKM_ADDRESS);
		return -2;
	}
	//mpu_config_bypass(fd, 1);
	//mpu_config_compass(fd, AKM_MODE_SINGLE);
	mpu_read_reg(fd, AKM_REG_STATUS_2, &val);
	
	val = 0;
	while ((val & 1) == 0) {
		mpu_read_reg(fd, AKM_REG_STATUS_1, &val);
		usleep(1000);
	}
	//printf("akm: 0x%x\n", val);
	mpu_read_chunk(fd, AKM_REG_DATA, buf, 6);

	data[0] = (int16_t)((buf[1] << 8) | buf[0]);
	data[1] = (int16_t)((buf[3] << 8) | buf[2]);
	data[2] = (int16_t)((buf[5] << 8) | buf[4]);
	//printf("compass: (%d, %d, %d)\n", data[0], data[1], data[2]);

	if (ioctl(fd, I2C_SLAVE, MPU_ADDRESS) < 0) {
		fprintf(stderr, "I2C: Failed to acquire bus access/talk to slave 0x%x\n", MPU_ADDRESS);
		return -2;
	}
	return 0;
}

int mpu_read_akm(int fd, uint8_t reg) {
	uint8_t val;

	if (ioctl(fd, I2C_SLAVE, AKM_ADDRESS) < 0) {
		fprintf(stderr, "I2C: Failed to acquire bus access/talk to slave 0x%x\n", AKM_ADDRESS);
		return -2;
	}
	mpu_read_reg(fd, reg, &val);

	printf("akm: 0x%x\n", val);

	if (ioctl(fd, I2C_SLAVE, MPU_ADDRESS) < 0) {
		fprintf(stderr, "I2C: Failed to acquire bus access/talk to slave 0x%x\n", MPU_ADDRESS);
		return -2;
	}
	return 0;
}