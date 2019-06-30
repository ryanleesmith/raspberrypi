class Sensor():
    WHO_AM_I_REG = 0x0F

    def __init__(self, bus, address, name):
        self.bus = bus
        self.address = address
        self.name = name

    def detect(self):
        try:
            print("Detecting %s..." % (self.name))
            resp = self.read(Sensor.WHO_AM_I_REG)
        except IOError as ioe:
            #raise IMUError(address)
            print("\nError")
        else:
            if (resp != self.WHO_AM_I):
                print("Unexpected: %s\n" % (resp))
                #raise IMUError(address)
            else:
                print("Found!\n")

    def read(self, register):
        return self.bus.read_byte_data(self.address, register)

    def write(self, register, value):
        self.bus.write_byte_data(self.address, register, value)
        return -1

class Accelerometer(Sensor):
    def __init__(self, bus):
        self.WHO_AM_I = 0x68
        Sensor.__init__(self, bus, 0x6A, "Accelerometer")

class Gyroscope(Sensor):
    def __init__(self, bus):
        self.WHO_AM_I = 0x68
        Sensor.__init__(self, bus, 0x6A, "Gyroscope")

class Magnetometer(Sensor):
    def __init__(self, bus):
        self.WHO_AM_I = 0x3D
        Sensor.__init__(self, bus, 0x1C, "Magnetometer")

class Thermostat(Sensor):
    def __init__(self, bus):
        self.WHO_AM_I = 0
        Sensor.__init__(self, bus, 0x77, "Thermostat")

class Barometer(Sensor):
    def __init__(self, bus):
        self.WHO_AM_I = 0
        Sensor.__init__(self, bus, 0x77, "Barometer")