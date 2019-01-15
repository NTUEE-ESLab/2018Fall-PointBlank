#ifndef DMP_H
#define DMP_H 1

#include <stdlib.h>
#include <stdint.h>
#include <sys/time.h>
#include "mpu.h"

/**
 *  Quaternion: math operation 
 */
typedef struct dmp_quaternion_t {
	float data[4]; /* w, x, y, z */
} dmp_quaternion;

void dmp_quaternion_init     (dmp_quaternion* q, float w, float x, float y, float z);
void dmp_quaternion_convert  (dmp_quaternion* q, int16_t *mpu_data, float unit);
void dmp_quaternion_conjugate(dmp_quaternion* q);
float dmp_quaternion_norm    (dmp_quaternion* q);

void dmp_quaternion_mul      (dmp_quaternion* q, dmp_quaternion* a, float m);
void dmp_quaternion_add      (dmp_quaternion* q, dmp_quaternion* a, dmp_quaternion* b);
void dmp_quaternion_sub      (dmp_quaternion* q, dmp_quaternion* a, dmp_quaternion* b);
void dmp_quaternion_product  (dmp_quaternion* q, dmp_quaternion* a, dmp_quaternion* b);
void dmp_quaternion_rotate   (dmp_quaternion* q, dmp_quaternion* r);


/** 
 *  Filter: Orientation observer & vibration reducer 
 */
#define DMP_EMIT_RATE       10
#define DMP_MOVE_THR        0.0    /* gyro, rad/s*/
#define DMP_OBSERVER_BETA   0.03

#define DMP_FILTER_IIR_DISCOUNT 0.98
#define DMP_FILTER_AVG_BUF_SIZE 32

void MadgwickAHRSupdateIMU(dmp_quaternion *q, dmp_quaternion *g, dmp_quaternion *a, float dt, float beta);

typedef struct dmp_filter_avg_t {
	int16_t         count;
	dmp_quaternion  buf[DMP_FILTER_AVG_BUF_SIZE];
} dmp_filter_avg;

typedef struct dmp_filter_iir_t {
	float           a;
	dmp_quaternion  buf;
} dmp_filter_iir;

void dmp_filter_iir_reset(dmp_filter_iir*);
void dmp_filter_iir_func(dmp_filter_iir*, dmp_quaternion *input, dmp_quaternion *output);


/** 
 *  MPU wrapper
 */
#define DMP_SLEEP       0x00
#define DMP_ACTIVE      0x01
#define DMP_SHUTDOWN    0xFF

#define DMP_GYRO_FS     MPU_GYRO_FS_2000
#define DMP_GYRO_DLPF   MPU_GYRO_DLPF_5
#define DMP_ACCEL_FS    MPU_ACCEL_FS_16
#define DMP_ACCEL_DLPF  MPU_ACCEL_DLPF_5

#define DMP_PROJECTION_SCALE  1.5

typedef struct dmp_mpu_t {
	int     fd;
	float   gyro_unit;    /* unit: rad/s per LSB */
	float   accel_unit;   /* unit: m/s2  per LSB */
	uint8_t state;
} dmp_mpu;

#define dmp_mpu_get_state(mpu) ((mpu)->state)

int dmp_mpu_init	(dmp_mpu*);
int dmp_mpu_finish	(dmp_mpu*);
int dmp_mpu_config	(dmp_mpu*, uint8_t state);
int dmp_mpu_read	(dmp_mpu*, dmp_quaternion *gyro, dmp_quaternion *accel);


/** 
 *  Dynamic Motion Processor
 */
typedef struct dmp_status_t {
	int             fifo_out;
	int             fifo_in;
	dmp_mpu         mpu;

	/* physical quantities */
	struct timeval  tv;
	dmp_filter_iir  filter_gyro;
	dmp_filter_iir  filter_accel;
	dmp_quaternion  rot_s2e;      /* rotation quaternion, from sensor to earth frame */
	dmp_quaternion  rot_e2b;      /* rotation quaternion, from earth to beginning frame  */

} dmp_status;

int dmp_init  (dmp_status*, char *fifo_out_name, char *fifo_in_name);
int dmp_finish(dmp_status*);
int dmp_run   (dmp_status*);

int dmp_begin_record(dmp_status*);
int dmp_update_record(dmp_status*);
int dmp_get_projection(dmp_status*, float* x, float *y);

#endif 