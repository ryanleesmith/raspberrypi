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

    def readBlock(self, register, size):
        return self.bus.read_i2c_block_data(self.address, register, size)

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

class Pressure(Sensor):
    def __init__(self, bus):
        self.WHO_AM_I = 0
        Sensor.__init__(self, bus, 0x77, "Pressure")
        self.readTrim()
        self.write(0xF4, 0x27)
        self.write(0xF5, 0xA0)

    def readTrim(self):
        self.trim = {}
        block = self.readBlock(0x88, 24)

        self.trim["T1"] = block[1] * 256 + block[0]
        self.trim["T2"] = block[3] * 256 + block[2]
        if self.trim["T2"] > 32767:
            self.trim["T2"] -= 65536
        self.trim["T3"] = block[5] * 256 + block[4]
        if self.trim["T3"] > 32767:
            self.trim["T3"] -= 65536

    def readTemp(self):
        data = self.readBlock(0xF7, 8)

        adc_t = ((data[3] * 65536) + (data[4] * 256) + (data[5] & 0xF0)) / 16

        var1 = ((adc_t) / 16384.0 - (self.trim["T1"]) / 1024.0) * (self.trim["T2"])
        var2 = (((adc_t) / 131072.0 - (self.trim["T1"]) / 8192.0) * ((adc_t)/131072.0 - (self.trim["T1"])/8192.0)) * (self.trim["T3"])
        #t_fine = (var1 + var2)
        cTemp = (var1 + var2) / 5120.0
        fTemp = cTemp * 1.8 + 32

        print "Temperature: %.2f F\n" % fTemp