import time
bus = "fake"
#import smbus
#bus = smbus.SMBus(1)

from IMU_REGISTERS import *
from sensors import sensor

acc = sensor.Accelerometer(bus)
gyr = sensor.Gyroscope(bus)
mag = sensor.Magnetometer(bus)
bar = sensor.Barometer(bus)

#///////////
#// Write //
#///////////
def write(address, register, value):
    bus.write_byte_data(address, register, value)
    return -1

def writeACC(register, value):
    return write(ACC_ADDRESS, register, value)

def writeMAG(register, value):
    return write(MAG_ADDRESS, register, value)

def writeGRY(register, value):
    return write(GYR_ADDRESS, register, value)

#//////////
#// Read //
#//////////
def read(address, register):
    return bus.read_byte_data(address, register)

def readACCx():
    acc_l = read(ACC_ADDRESS, OUT_X_L_XL)
    acc_h = read(ACC_ADDRESS, OUT_X_H_XL)
    acc_combined = (acc_l | acc_h <<8)

    return acc_combined if acc_combined < 32768 else acc_combined - 65536

def readACCy():
    acc_l = read(ACC_ADDRESS, OUT_Y_L_XL)
    acc_h = read(ACC_ADDRESS, OUT_Y_H_XL)
    acc_combined = (acc_l | acc_h <<8)

    return acc_combined if acc_combined < 32768 else acc_combined - 65536

def readACCz():
    acc_l = read(ACC_ADDRESS, OUT_Z_L_XL)
    acc_h = read(ACC_ADDRESS, OUT_Z_H_XL)
    acc_combined = (acc_l | acc_h <<8)

    return acc_combined if acc_combined < 32768 else acc_combined - 65536

def readMAGx():
    mag_l = read(MAG_ADDRESS, OUT_X_L_M)
    mag_h = read(MAG_ADDRESS, OUT_X_H_M)
    mag_combined = (mag_l | mag_h <<8)

    return mag_combined if mag_combined < 32768 else mag_combined - 65536

def readMAGy():
    mag_l = read(MAG_ADDRESS, OUT_Y_L_M)
    mag_h = read(MAG_ADDRESS, OUT_Y_H_M)
    mag_combined = (mag_l | mag_h <<8)

    return mag_combined if mag_combined < 32768 else mag_combined - 65536

def readMAGz():
    mag_l = read(MAG_ADDRESS, OUT_Z_L_M)
    mag_h = read(MAG_ADDRESS, OUT_Z_H_M)
    mag_combined = (mag_l | mag_h <<8)

    return mag_combined if mag_combined < 32768 else mag_combined - 65536

def readGYRx():
    gyr_l = read(GYR_ADDRESS, OUT_X_L_G)
    gyr_h = read(GYR_ADDRESS, OUT_X_H_G)
    gyr_combined = (gyr_l | gyr_h <<8)

    return gyr_combined if gyr_combined < 32768 else gyr_combined - 65536

def readGYRy():
    gyr_l = read(GYR_ADDRESS, OUT_Y_L_G)
    gyr_h = read(GYR_ADDRESS, OUT_Y_H_G)
    gyr_combined = (gyr_l | gyr_h <<8)

    return gyr_combined if gyr_combined < 32768 else gyr_combined - 65536

def readGYRz():
    gyr_l = read(GYR_ADDRESS, OUT_Z_L_G)
    gyr_h = read(GYR_ADDRESS, OUT_Z_H_G)
    gyr_combined = (gyr_l | gyr_h <<8)

    return gyr_combined if gyr_combined < 32768 else gyr_combined - 65536

#//////////
#// Init //
#//////////
class Error(Exception):
    pass

class IMUError(Error):
    def __init__(self, address):
        self.address = address

def detect(address, expectedResp):
    try:
        print("\nDetecting %s..." % (NAMES[address]))
        resp = read(address, WHO_AM_I_REG)
    except IOError as ioe:
        raise IMUError(address)
    else:
        print("\nGot: %s" % (resp))
        if (resp != expectedResp):
            print("\nUnexpected: %s" % (expectedResp))
            raise IMUError(address)

def detectImu():
    global acc, gyr, mag, bar
    acc.detect()
    gyr.detect()
    mag.detect()
    bar.detect()

    return

    gyr = Gyroscope()
    mag = Magnetometer()

    try:
        detect(ACC_ADDRESS, WHO_AM_I_A_RESP)
        detect(GYR_ADDRESS, WHO_AM_I_G_RESP)
        detect(MAG_ADDRESS, WHO_AM_I_M_RESP)
        detect(PRS_ADDRESS, 0)
    except IMUError as imue:
        print("\nCould not detect %s" % (NAMES[imue.address]))
    else:
        print "\nDetected IMU"

    time.sleep(1)

def init():
    return

    # Init accelerometer
    writeACC(CTRL_REG5_XL, 0b00111000)  #z, y, x axis enabled for accelerometer
    writeACC(CTRL_REG6_XL, 0b00101000)  #+/- 16g

    # Init gyroscope
    writeGRY(CTRL_REG4, 0b00111000)     #z, y, x axis enabled for gyro
    writeGRY(CTRL_REG1_G, 0b10111000)   #Gyro ODR = 476Hz, 2000 dps
    writeGRY(ORIENT_CFG_G, 0b00111000)  #Swap orientation 

    # Init magnetometer
    writeMAG(CTRL_REG1_M, 0b10011100)   #Temp compensation enabled,Low power mode mode,80Hz ODR
    writeMAG(CTRL_REG2_M, 0b01000000)   #+/-12gauss
    writeMAG(CTRL_REG3_M, 0b00000000)   #continuos update
    writeMAG(CTRL_REG4_M, 0b00000000)   #lower power mode for Z axis