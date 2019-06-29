class Gyroscope(Sensor):
    def __init__(self):
        Sensor.__init__(self, 0x6A, "Gyroscope")