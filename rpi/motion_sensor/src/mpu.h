#ifndef MPU_H
#define MPU_H 1

#include <stdlib.h>
#include <stdint.h>
#include "mpu_const.h"

/* mpu API */
#define MPU_CONVERT_GYRO_FS(fs)    ((float)(125 << (fs+1))) /* output unit: degree */
#define MPU_CONVERT_ACCEL_FS(fs)   ((float)((1 << (fs+1))))   /* output unit: g */
#define MPU_CONVERT_COMPASS_FS(fs) 4800.0           /* output unit: uT */

/* mpu file API */
int mpu_open();
int mpu_close(int fd);

/* mpu register read / write API */
int mpu_read_reg   (int fd, uint8_t reg, uint8_t *val);
int mpu_write_reg  (int fd, uint8_t reg, uint8_t val);
int mpu_read_chunk (int fd, uint8_t reg, uint8_t *buf, size_t size);
int mpu_write_chunk(int fd, uint8_t reg, uint8_t *buf, size_t size);

/* mpu configuration API */
int mpu_config_gyro_fs(int fd, uint8_t fullscale);
int mpu_config_gyro_dlpf(int fd, uint8_t dlpf);
int mpu_config_accel_fs(int fd, uint8_t fullscale);
int mpu_config_accel_dlpf(int fd, uint8_t dlpf);
int mpu_config_bypass(int fd, uint8_t enable);
int mpu_config_compass(int fd, uint8_t mode);

/* mpu high-level configuration API */
int mpu_config_reset(int fd);
int mpu_config_sleep(int fd);
int mpu_config_low_power(int fd, uint8_t wom_thr, uint8_t mpu_lposc_clk);
int mpu_config_full_power(int fd, uint8_t gyro_fs, uint8_t gyro_dlpf, uint8_t accel_fs, uint8_t accel_dlpf);


int mpu_read_gyro(int fd, int16_t *data);
int mpu_read_accel(int fd, int16_t *data);
int mpu_read_compass(int fd, int16_t *data);
int mpu_read_akm(int fd, uint8_t reg);

#endif 
