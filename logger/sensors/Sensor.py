class Sensor():
    WHO_AM_I_REG = 0x0F

    def __init__(self, bus, address, name):
        self.bus = bus
        self.address = address
        self.name = name

    def detect(self):
        try:
            print("\nDetecting %s..." % (self.name))
            resp = self.read(Sensor.WHO_AM_I_REG)
        except IOError as ioe:
            #raise IMUError(address)
            print("\nError")
        else:
            print("\nGot: %s" % (resp))
            if (False):
                print("\nUnexpected: %s" % (expectedResp))
                #raise IMUError(address)

    def read(self, register):
        return self.bus.read_byte_data(self.address, register)

    def write(self, register, value):
        self.bus.write_byte_data(self.address, register, value)
        return -1

class Accelerometer(Sensor):
    def __init__(self, bus):
        Sensor.__init__(self, bus, 0x6A, "Accelerometer")