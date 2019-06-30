import time
import smbus
bus = smbus.SMBus(1)

from sensors import sensor

acc = sensor.Accelerometer(bus)
gyr = sensor.Gyroscope(bus)
mag = sensor.Magnetometer(bus)
tmp = sensor.Thermostat(bus)

def detect():
    global acc, gyr, mag, tmp
    try:
        acc.detect()
        gyr.detect()
        mag.detect()
        tmp.detect()
    except sensor.SensorError as e:
        print "Could not detect %s\n" % e.name
        return False
    else:
        return True

def initialize():
    global acc, gyr, mag, tmp
    acc.initialize()
    gyr.initialize()
    mag.initialize()
    tmp.initialize()

    print "\n"
    return

def printData():
    global tmp
    tmp.readTemp()