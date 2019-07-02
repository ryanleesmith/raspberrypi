import time
import smbus
bus = smbus.SMBus(1)

from sensors import sensor

acc = sensor.Accelerometer(bus)
gyr = sensor.Gyroscope(bus)
mag = sensor.Magnetometer(bus)
tmp = sensor.Thermostat(bus)
bar = sensor.Barometer(bus)

def detect():
    global acc, gyr, mag, tmp, bar
    try:
        acc.detect()
        gyr.detect()
        mag.detect()
        tmp.detect()
        bar.detect()
    except sensor.SensorError as e:
        print "Could not detect %s\n" % e.name
        return False
    else:
        return True

def initialize():
    global acc, gyr, mag, tmp, bar
    acc.initialize()
    gyr.initialize()
    mag.initialize()
    tmp.initialize()
    bar.initialize()
    return

def printData():
    global tmp, bar
    print(tmp)
    print(bar)