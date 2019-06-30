class Sensor():
    WHO_AM_I_REG = 0x0F

    def __init__(self, bus, address, name):
        self.bus = bus
        self.address = address
        self.name = name

    def detect():
        try:
            print("\nDetecting %s..." % (self.name))
            resp = self.read(WHO_AM_I_REG)
        except IOError as ioe:
            #raise IMUError(address)
            print("\nError")
        else:
            print("\nGot: %s" % (resp))
            if (False):
                print("\nUnexpected: %s" % (expectedResp))
                #raise IMUError(address)

    def read(register):
        return self.bus.read_byte_data(self.address, register)

    def write(register, value):
        self.bus.write_byte_data(self.address, register, value)
        return -1