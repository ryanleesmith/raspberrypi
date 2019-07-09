import time
import smbus
bus = smbus.SMBus(1)

from sensors import sensor

acc = sensor.Accelerometer(bus)
gyr = sensor.Gyroscope(bus)
mag = sensor.Magnetometer(bus)
thm = sensor.Thermometer(bus)
bar = sensor.Barometer(bus)
alt = sensor.Altimeter(bus)

def detect():
    global acc, gyr, mag, thm, bar, alt
    try:
        acc.detect()
        gyr.detect()
        mag.detect()
        thm.detect()
        bar.detect()
        alt.detect()
    except sensor.SensorError as e:
        print "Could not detect %s\n" % e.name
        return False
    else:
        return True

def initialize():
    global acc, gyr, mag, thm, bar, alt
    acc.initialize()
    gyr.initialize()
    mag.initialize()
    thm.initialize()
    bar.initialize()
    alt.initialize()
    return

def printData():
    global acc, gyr, thm, bar, alt
    print(acc)
    print(gyr)
    print(thm)
    print(bar)
    print(alt)