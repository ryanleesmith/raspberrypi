import time
import smbus
bus = smbus.SMBus(1)

from sensors import sensor

imu = sensor.IMU(bus)
thm = sensor.Thermometer(bus)
bar = sensor.Barometer(bus)
alt = sensor.Altimeter(bus)

def detect():
    global imu, thm, bar, alt
    try:
        imu.detect()
        thm.detect()
        bar.detect()
        alt.detect()
    except sensor.SensorError as e:
        print("Could not detect %s\n" % e.name)
        return False
    else:
        return True

def initialize():
    global imu, thm, bar, alt
    imu.initialize()
    thm.initialize()
    bar.initialize()
    alt.initialize()
    return

def printData():
    global imu, thm, bar, alt
    print(imu)
    print(thm)
    print(bar)
    print(alt)