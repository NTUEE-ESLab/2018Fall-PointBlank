#ifndef MPU_CONST_H
#define MPU_CONST_H 1

#define I2C_FILENAME "/dev/i2c-1"
#define MPU_ADDRESS 0x68  
#define AKM_ADDRESS 0x0C  /* AK compass */


/* mpu register map */ 
enum mpu_reg {
	MPU_REG_SMPLRT_DIV     = 0x19,
	MPU_REG_CONFIG         = 0x1A,
	MPU_REG_GYRO_CONFIG    = 0x1B,
	MPU_REG_ACCEL_CONFIG   = 0x1C,
	MPU_REG_ACCEL_CONFIG_2 = 0x1D,
	MPU_LP_ACCEL_ODR       = 0x1E,
	MPU_WOM_THR            = 0x1F, 

	MPU_INT_PIN_CFG        = 0x37, // and i2c bypass_en
	MPU_INT_ENABLE         = 0x38,
	MPU_INT_STATUS         = 0x39,

	MPU_REG_ACCEL          = 0x3B,
	MPU_REG_TEMP           = 0x41,
	MPU_REG_GYRO           = 0x43,

	MPU_MOT_DETECT_CTRL    = 0x69,
	MPU_USER_CTRL          = 0x6A,
	MPU_REG_PWR_MGMT_1     = 0x6B,
	MPU_REG_PWR_MGMT_2     = 0x6C
};

enum mpu_gyro_fullscale {
	MPU_GYRO_FS_250  = 0,
	MPU_GYRO_FS_500  = 1,
	MPU_GYRO_FS_1000 = 2,
	MPU_GYRO_FS_2000 = 3
};

enum mpu_accel_fullscale {
	MPU_ACCEL_FS_2  = 0,
	MPU_ACCEL_FS_4  = 1,
	MPU_ACCEL_FS_8  = 2,
	MPU_ACCEL_FS_16 = 3
};

enum mpu_gyro_dlpf {
	MPU_GYRO_DLPF_250  = 0,
	MPU_GYRO_DLPF_184  = 1,
	MPU_GYRO_DLPF_92   = 2,
	MPU_GYRO_DLPF_41   = 3,
	MPU_GYRO_DLPF_20   = 4,
	MPU_GYRO_DLPF_10   = 5,
	MPU_GYRO_DLPF_5    = 6,
	MPU_GYRO_DLPF_3600 = 7, 
	MPU_GYRO_DLPF_DEF1 = 0xFE,   // default DLFP 1: BW = 3600 Hz 
	MPU_GYRO_DLPF_DEF0 = 0xFF    // default DLFP 0: BW = 8800 Hz
};

enum mpu_accel_dlpf {
	MPU_ACCEL_DLPF_218 = 0,      
	MPU_ACCEL_DLPF_184 = 1,      // wrong in data sheet (218 Hz)
	MPU_ACCEL_DLPF_99  = 2,
	MPU_ACCEL_DLPF_45  = 3,
	MPU_ACCEL_DLPF_21  = 4,
	MPU_ACCEL_DLPF_10  = 5,
	MPU_ACCEL_DLPF_5   = 6,
	MPU_ACCEL_DLPF_420 = 7, 
	MPU_ACCEL_DLPF_DEF = 0xFF    // 1046 Hz
};

enum mpu_lposc_clk {
	MPU_LPOSC_CLK_0_24  = 0,      
	MPU_LPOSC_CLK_0_49  = 1, 
	MPU_LPOSC_CLK_0_98  = 2,
	MPU_LPOSC_CLK_1_95  = 3,
	MPU_LPOSC_CLK_3_91  = 4,
	MPU_LPOSC_CLK_7_81  = 5,
	MPU_LPOSC_CLK_15_63 = 6,
	MPU_LPOSC_CLK_31_25 = 7, 
	MPU_LPOSC_CLK_62_5  = 8,
	MPU_LPOSC_CLK_125   = 9,
	MPU_LPOSC_CLK_250   = 10,
	MPU_LPOSC_CLK_500   = 11    
};


/* akm register map */
enum akm_reg {
	AKM_REG_DEVICE_ID   = 0x00,
	AKM_REG_DEVICE_INFO	= 0x01,
	AKM_REG_STATUS_1	= 0x02,
	AKM_REG_DATA		= 0x03,
	AKM_REG_STATUS_2	= 0x09,
	AKM_REG_CONTROL_1	= 0x0A,
	AKM_REG_CONTROL_2	= 0x0B,
	AKM_REG_OFFSET		= 0x10
};

enum akm_mode {
	AKM_MODE_POWER_DOWN = 0x0,	
	AKM_MODE_SINGLE     = 0x1, // single measurement, return to POWER_DOWN automatically
	AKM_MODE_CONT_8HZ   = 0x2, // continuous measurement, 8Hz
	AKM_MODE_CONT_100HZ = 0x6, // continuous measurement, 100Hz
	AKM_MODE_EXT_TRIGGER= 0x4, // measure one time by external trigger 
	AKM_MODE_SELF_TEST  = 0x8, 
	AKM_MODE_FUSE_ROM   = 0xF 
};

#endif 