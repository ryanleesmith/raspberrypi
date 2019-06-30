from Sensor import Sensor

class Accelerometer(Sensor):
    def __init__(self, bus):
        Sensor.__init__(self, bus, 0x6A, "Accelerometer")