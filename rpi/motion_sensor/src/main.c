#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <math.h>
#include <errno.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include "dmp.h"

#define DMP_FIFO_OUT "/tmp/server_in.pipe"
#define DMP_FIFO_IN  "/tmp/server_out.pipe"

int point_blank() {
	dmp_status dmp;

	dmp_init(&dmp, DMP_FIFO_OUT, DMP_FIFO_IN);
	dmp_run(&dmp);
	dmp_finish(&dmp);

	return 0;
}

int main(){
	return point_blank();
}
