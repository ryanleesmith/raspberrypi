class Sensor():
    def __init__(self, bus, address, id, name):
        self.idRegister = 0x0F
        self.bus = bus
        self.address = address
        self.id = id
        self.name = name

    def detect(self):
        try:
            print("Detecting %s..." % (self.name))
            id = self.read(self.idRegister)
        except IOError as ioe:
            raise SensorError(self.name)
        else:
            if (id != self.id):
                raise SensorError(self.name)
            else:
                print("Found!\n")

    def initialize(self):
        print("Initialized %s" % (self.name))
        return

    def read(self, register):
        return self.bus.read_byte_data(self.address, register)

    def readBlock(self, register, size):
        return self.bus.read_i2c_block_data(self.address, register, size)

    def write(self, register, value):
        self.bus.write_byte_data(self.address, register, value)
        return -1

class Accelerometer(Sensor):
    def __init__(self, bus):
        Sensor.__init__(self, bus, 0x6A, 0x68, "Accelerometer")

class Gyroscope(Sensor):
    def __init__(self, bus):
        Sensor.__init__(self, bus, 0x6A, 0x68, "Gyroscope")

class Magnetometer(Sensor):
    def __init__(self, bus):
        Sensor.__init__(self, bus, 0x1C, 0x3D, "Magnetometer")

class Pressure(Sensor):
    def __init__(self, bus, name):
        Sensor.__init__(self, bus, 0x77, 0x58, name)
        self.idRegister = 0xD0

    def initialize(self):
        self.readTrim()
        self.write(0xF4, 0x27)
        self.write(0xF5, 0xA0)
        Sensor.initialize(self)

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

class Thermostat(Pressure):
    def __init__(self, bus):
        Pressure.__init__(self, bus, "Thermostat")

    def readTemp(self):
        data = self.readBlock(0xF7, 8)

        adc_t = ((data[3] * 65536) + (data[4] * 256) + (data[5] & 0xF0)) / 16

        var1 = ((adc_t) / 16384.0 - (self.trim["T1"]) / 1024.0) * (self.trim["T2"])
        var2 = (((adc_t) / 131072.0 - (self.trim["T1"]) / 8192.0) * ((adc_t)/131072.0 - (self.trim["T1"])/8192.0)) * (self.trim["T3"])
        #t_fine = (var1 + var2)
        cTemp = (var1 + var2) / 5120.0
        return cTemp * 1.8 + 32

    def __str__(self):
        return "Temperature: %.2f F\n" % self.readTemp()


class SensorError(Exception):
    def __init__(self, name):
        self.name = name