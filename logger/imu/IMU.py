import time
import smbus
bus = smbus.SMBus(1)

from sensors import sensor

acc = sensor.Accelerometer(bus)
gyr = sensor.Gyroscope(bus)
mag = sensor.Magnetometer(bus)
thm = sensor.Thermometer(bus)
bar = sensor.Barometer(bus)

def detect():
    global acc, gyr, mag, thm, bar
    try:
        acc.detect()
        gyr.detect()
        mag.detect()
        thm.detect()
        bar.detect()
    except sensor.SensorError as e:
        print "Could not detect %s\n" % e.name
        return False
    else:
        return True

def initialize():
    global acc, gyr, mag, thm, bar
    acc.initialize()
    gyr.initialize()
    mag.initialize()
    thm.initialize()
    bar.initialize()
    return

def printData():
    global thm, bar
    print(thm)
    print(bar)