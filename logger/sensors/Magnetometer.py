class Magnetometer(Sensor):
    def __init__(self):
        Sensor.__init__(self, 0x1C, "Magnetometer")