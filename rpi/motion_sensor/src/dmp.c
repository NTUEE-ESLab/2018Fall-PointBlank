#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <errno.h>
#include <unistd.h>
#include <sys/time.h>
#include <sys/ioctl.h>
#include <wiringPi.h>
#include <fcntl.h>
#include "dmp.h"


void dmp_quaternion_init(dmp_quaternion *q, float w, float x, float y, float z) {
	q->data[0] = w;
	q->data[1] = x;
	q->data[2] = y;
	q->data[3] = z;
}

void dmp_quaternion_convert(dmp_quaternion* q, int16_t *data, float resolution) {
	uint8_t i;
	q->data[0] = 0.0;
	for (i = 0; i < 3; ++i) q->data[i+1] = data[i] * resolution;
}

void dmp_quaternion_conjugate(dmp_quaternion* q) {
	q->data[1] = -(q->data[1]);
	q->data[2] = -(q->data[2]);
	q->data[3] = -(q->data[3]);
}

float dmp_quaternion_norm(dmp_quaternion* q) {
	return (float)sqrt(q->data[0] * q->data[0] + q->data[1] * q->data[1] 
		             + q->data[2] * q->data[2] + q->data[3] * q->data[3]);
}

void dmp_quaternion_mul(dmp_quaternion* q, dmp_quaternion* a, float m) {
	uint8_t i;
	for (i = 0; i < 4; ++i) q->data[i] = m * a->data[i];
}

void dmp_quaternion_add(dmp_quaternion* q, dmp_quaternion* a, dmp_quaternion* b) {
	uint8_t i;
	for (i = 0; i < 4; ++i) q->data[i] = a->data[i] + b->data[i];
}

void dmp_quaternion_sub(dmp_quaternion* q, dmp_quaternion* a, dmp_quaternion* b) {
	uint8_t i;
	for (i = 0; i < 4; ++i) q->data[i] = a->data[i] - b->data[i];
}

void dmp_quaternion_product(dmp_quaternion* q, dmp_quaternion* a, dmp_quaternion* b) {
	q->data[0] = a->data[0] * b->data[0] - a->data[1] * b->data[1] 
			   - a->data[2] * b->data[2] - a->data[3] * b->data[3];

	q->data[1] = a->data[0] * b->data[1] + a->data[1] * b->data[0] 
			   + a->data[2] * b->data[3] - a->data[3] * b->data[2];

	q->data[2] = a->data[0] * b->data[2] - a->data[1] * b->data[3] 
			   + a->data[2] * b->data[0] + a->data[3] * b->data[1];

	q->data[3] = a->data[0] * b->data[3] + a->data[1] * b->data[2] 
			   - a->data[2] * b->data[1] + a->data[3] * b->data[0];
}

void dmp_quaternion_rotate(dmp_quaternion* q, dmp_quaternion* r) {
	dmp_quaternion tmp;
	dmp_quaternion_conjugate(r);
	dmp_quaternion_product(&tmp, q, r);
	dmp_quaternion_conjugate(r);
	dmp_quaternion_product(q, r, &tmp);
}

// Fast inverse square-root
// See: http://en.wikipedia.org/wiki/Fast_inverse_square_root
float invSqrt(float x) {
	float halfx = 0.5f * x;
	float y = x;
	long i = *(long*)&y;
	i = 0x5f3759df - (i>>1);
	y = *(float*)&i;
	y = y * (1.5f - (halfx * y * y));
	return y;
}

// Implementation of Madgwick's IMU and AHRS algorithms.
// See: http://www.x-io.co.uk/node/8#open_source_ahrs_and_imu_algorithms
//
// Date			Author          Notes
// 29/09/2011	SOH Madgwick    Initial release
// 02/10/2011	SOH Madgwick	Optimised for reduced CPU load
// 19/02/2012	SOH Madgwick	Magnetometer measurement is normalised
//
void MadgwickAHRSupdateIMU(dmp_quaternion *q, dmp_quaternion *g, dmp_quaternion *a, float dt, float beta) {
	float recipNorm;
	float s0, s1, s2, s3;
	float qDot1, qDot2, qDot3, qDot4;
	float _2q0, _2q1, _2q2, _2q3, _4q0, _4q1, _4q2 ,_8q1, _8q2, q0q0, q1q1, q2q2, q3q3;

	// Cache of variable
	float q0 = q->data[0], q1 = q->data[1], q2 = q->data[2], q3 = q->data[3];
	float gx = g->data[1], gy = g->data[2], gz = g->data[3];
	float ax = a->data[1], ay = a->data[2], az = a->data[3];

	// Rate of change of quaternion from gyroscope
	qDot1 = 0.5f * (-q1 * gx - q2 * gy - q3 * gz);
	qDot2 = 0.5f * (q0 * gx + q2 * gz - q3 * gy);
	qDot3 = 0.5f * (q0 * gy - q1 * gz + q3 * gx);
	qDot4 = 0.5f * (q0 * gz + q1 * gy - q2 * gx);

	// Compute feedback only if accelerometer measurement valid (avoids NaN in accelerometer normalisation)
	if(!((ax == 0.0f) && (ay == 0.0f) && (az == 0.0f))) {

		// Normalise accelerometer measurement
		recipNorm = invSqrt(ax * ax + ay * ay + az * az);
		ax *= recipNorm;
		ay *= recipNorm;
		az *= recipNorm;   

		// Auxiliary variables to avoid repeated arithmetic
		_2q0 = 2.0f * q0;
		_2q1 = 2.0f * q1;
		_2q2 = 2.0f * q2;
		_2q3 = 2.0f * q3;
		_4q0 = 4.0f * q0;
		_4q1 = 4.0f * q1;
		_4q2 = 4.0f * q2;
		_8q1 = 8.0f * q1;
		_8q2 = 8.0f * q2;
		q0q0 = q0 * q0;
		q1q1 = q1 * q1;
		q2q2 = q2 * q2;
		q3q3 = q3 * q3;

		// Gradient decent algorithm corrective step
		s0 = _4q0 * q2q2 + _2q2 * ax + _4q0 * q1q1 - _2q1 * ay;
		s1 = _4q1 * q3q3 - _2q3 * ax + 4.0f * q0q0 * q1 - _2q0 * ay - _4q1 + _8q1 * q1q1 + _8q1 * q2q2 + _4q1 * az;
		s2 = 4.0f * q0q0 * q2 + _2q0 * ax + _4q2 * q3q3 - _2q3 * ay - _4q2 + _8q2 * q1q1 + _8q2 * q2q2 + _4q2 * az;
		s3 = 4.0f * q1q1 * q3 - _2q1 * ax + 4.0f * q2q2 * q3 - _2q2 * ay;
		recipNorm = invSqrt(s0 * s0 + s1 * s1 + s2 * s2 + s3 * s3); // normalise step magnitude
		s0 *= recipNorm;
		s1 *= recipNorm;
		s2 *= recipNorm;
		s3 *= recipNorm;

		// Apply feedback step
		qDot1 -= beta * s0;
		qDot2 -= beta * s1;
		qDot3 -= beta * s2;
		qDot4 -= beta * s3;
	}

	// Integrate rate of change of quaternion to yield quaternion
	q0 += qDot1 * (1.0f * dt);
	q1 += qDot2 * (1.0f * dt);
	q2 += qDot3 * (1.0f * dt);
	q3 += qDot4 * (1.0f * dt);

	// Normalise quaternion
	recipNorm = invSqrt(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3);
	q0 *= recipNorm;
	q1 *= recipNorm;
	q2 *= recipNorm;
	q3 *= recipNorm;

	// Write back
	q->data[0] = q0;
	q->data[1] = q1;
	q->data[2] = q2;
	q->data[3] = q3;
}


void dmp_filter_iir_reset(dmp_filter_iir *filter) {
	filter->a = DMP_FILTER_IIR_DISCOUNT;
	dmp_quaternion_init(&filter->buf, 0, 0, 0, 0);
	//memset(&filter->buf, 0, sizeof(dmp_quaternion));
}

void dmp_filter_iir_func(dmp_filter_iir *filter, dmp_quaternion *input, dmp_quaternion *output) {
	dmp_quaternion_mul(&filter->buf, &filter->buf, filter->a);
	dmp_quaternion_mul(output, input, 1 - filter->a);
	dmp_quaternion_add(output, output, &filter->buf);

	memcpy(&filter->buf, output, sizeof(dmp_quaternion));
}


int dmp_mpu_init(dmp_mpu *mpu) {
	mpu->fd         = mpu_open();
	mpu->gyro_unit  = MPU_CONVERT_GYRO_FS(DMP_GYRO_FS) * (M_PI / 180.0) / (float)INT16_MAX;
	mpu->accel_unit = MPU_CONVERT_ACCEL_FS(DMP_ACCEL_FS) * 9.8 / (float)INT16_MAX;
	mpu->state      = DMP_SLEEP;

	mpu_config_reset(mpu->fd);
	mpu_config_bypass(mpu->fd, 0);
	mpu_config_sleep(mpu->fd);
	return 0;
}

int dmp_mpu_finish(dmp_mpu *mpu) {
	mpu_close(mpu->fd);
	return 0;
}

int dmp_mpu_config(dmp_mpu *mpu, uint8_t state) {
	if      (state == DMP_SLEEP ) mpu_config_sleep(mpu->fd); 
	else if (state == DMP_ACTIVE) mpu_config_full_power(mpu->fd, DMP_GYRO_FS, DMP_GYRO_DLPF, DMP_ACCEL_FS, DMP_ACCEL_DLPF); 
	mpu->state = state;
	return 0;
}

int dmp_mpu_read(dmp_mpu *mpu, dmp_quaternion *gyro, dmp_quaternion *accel) {
	int16_t data[3];

	mpu_read_gyro(mpu->fd, &data[0]);
	dmp_quaternion_convert(gyro, &data[0], mpu->gyro_unit);

	mpu_read_accel(mpu->fd, &data[0]);
	dmp_quaternion_convert(accel, &data[0], mpu->accel_unit);

	return 0;
}



int dmp_init(dmp_status *dmp, char *fifo_out_name, char *fifo_in_name) {
	if ((dmp->fifo_out = open(fifo_out_name, O_WRONLY)) < 0) {
		perror("fifo_out open error\n");
	}
	if ((dmp->fifo_in = open(fifo_in_name,  O_RDONLY | O_NONBLOCK)) < 0) {
		perror("fifo_in open error\n");
	}
	dmp_mpu_init(&dmp->mpu);

	return 0;
}

int dmp_finish(dmp_status *dmp) {
	dmp_mpu_finish(&dmp->mpu);
	if(dmp->fifo_in  >= 0) close(dmp->fifo_in);
	if(dmp->fifo_out >= 0) close(dmp->fifo_out);

	return 0;
}

int fd_set_nonblock(int fd, int nonblock) {
	int flags = fcntl(fd, F_GETFL, 0);
	if (flags == -1) return 0;

    if (nonblock) flags |=  O_NONBLOCK;
    else          flags &= ~O_NONBLOCK;
    return fcntl(fd, F_SETFL, flags) != -1;
}

int dmp_run(dmp_status *dmp) {
	uint8_t state = dmp_mpu_get_state(&dmp->mpu);
	float   point[2];

	while (state != DMP_SHUTDOWN) {
		if (state == DMP_SLEEP) {
			printf("idle\n");
			fd_set_nonblock(dmp->fifo_in, 0);
			read(dmp->fifo_in, &state, 1);

			if (state == DMP_ACTIVE) {
				printf("active\n");
				fd_set_nonblock(dmp->fifo_in, 1);
				dmp_mpu_config(&dmp->mpu, state);
				dmp_begin_record(dmp);
			} 
		}
		else {
			dmp_update_record(dmp);
			dmp_get_projection(dmp, &point[0], &point[1]);
			//printf("point = (%f, %f)\n", point[0], point[1]);
			write(dmp->fifo_out, &point[0], 2 * sizeof(float));
			read(dmp->fifo_in, &state, 1);
			if (state == DMP_SLEEP) dmp_mpu_config(&dmp->mpu, state);
		}
	}
	printf("end\n");
	return 0;
}

int dmp_begin_record(dmp_status *dmp) {
	float   norm, cos_theta, cos_theta_2, sin_theta_2;
	dmp_quaternion gyro, accel, rot_tmp;

	// time & filter
	gettimeofday(&dmp->tv, NULL);
	dmp_filter_iir_reset(&dmp->filter_gyro);
	dmp_filter_iir_reset(&dmp->filter_accel);

	// s to b
	dmp_mpu_read(&dmp->mpu, &gyro, &accel);
	norm      = sqrt(accel.data[1] * accel.data[1] + accel.data[3] * accel.data[3]);
	cos_theta = accel.data[3] / norm;
	cos_theta_2 = sqrt(0.5 * (1 + cos_theta));
	sin_theta_2 = sqrt(0.5 * (1 - cos_theta));
	if (accel.data[1] < 0.0) sin_theta_2 = -sin_theta_2;
	dmp_quaternion_init(&rot_tmp, cos_theta_2, 0.0, -sin_theta_2, 0.0);

	// b to e
	dmp_quaternion_rotate(&accel, &rot_tmp);
	norm      = sqrt(accel.data[2] * accel.data[2] + accel.data[3] * accel.data[3]);
	cos_theta = accel.data[3] / norm;
	cos_theta_2 = sqrt(0.5 * (1 + cos_theta)); 
	sin_theta_2 = sqrt(0.5 * (1 - cos_theta));
	if (accel.data[2] > 0.0) sin_theta_2 = -sin_theta_2;
	dmp_quaternion_init(&dmp->rot_e2b, cos_theta_2, -sin_theta_2, 0.0, 0.0);

	// write back
	dmp_quaternion_product(&dmp->rot_s2e, &dmp->rot_e2b, &rot_tmp);
	dmp_quaternion_conjugate(&dmp->rot_e2b);

	return 0;
}

int dmp_update_record(dmp_status *dmp) {
	uint8_t        count;
	float          dt, norm;
	struct timeval new_tv;
	dmp_quaternion gyro, accel;

	for (count = 0; count < DMP_EMIT_RATE; ++count) {
		gettimeofday(&new_tv, NULL);
		dmp_mpu_read(&dmp->mpu, &gyro, &accel);
		dmp_filter_iir_func(&dmp->filter_gyro, &gyro, &gyro);
		dmp_filter_iir_func(&dmp->filter_accel, &accel, &accel);

		norm = dmp_quaternion_norm(&gyro);
		printf("gyro_norm = %f\n", norm);
		if (norm > DMP_MOVE_THR) {
			dt = (float)(1e6 * (new_tv.tv_sec - dmp->tv.tv_sec) + (new_tv.tv_usec - dmp->tv.tv_usec)) * 1e-6;
			MadgwickAHRSupdateIMU(&dmp->rot_s2e, &gyro, &accel, dt, DMP_OBSERVER_BETA);
		}
		memcpy(&dmp->tv, &new_tv, sizeof(struct timeval));
	}
	return 0;
}

int dmp_get_projection(dmp_status *dmp, float* x, float *y) {
	dmp_quaternion direct;
	float tmp_x, tmp_y;

	dmp_quaternion_init(&direct, 0, 0, 1, 0);
	dmp_quaternion_rotate(&direct, &dmp->rot_s2e);
	dmp_quaternion_rotate(&direct, &dmp->rot_e2b);

	tmp_x = -direct.data[1] + 0.5;
	if (tmp_x < 0.0) tmp_x = 0.0;
	if (tmp_x > 1.0) tmp_x = 1.0;

	tmp_y = direct.data[3] + 0.5;
	if (tmp_y < 0.0) tmp_y = 0.0;
	if (tmp_y > 1.0) tmp_y = 1.0;

	*x = tmp_x;
	*y = tmp_y;
	return 0;
}