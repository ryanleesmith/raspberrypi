class Accelerometer(Sensor):
    def __init__(self):
        Sensor.__init__(self, 0x6A, "Accelerometer")