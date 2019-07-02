from time import time

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
    trim = {}
    data = []
    tFine = 0
    lastRead = 0

    def __init__(self, bus, name):
        Sensor.__init__(self, bus, 0x77, 0x58, name)
        self.idRegister = 0xD0

    def initialize(self):
        self.readTrim()
        self.write(0xF4, 0x27)
        self.write(0xF5, 0xA0)
        Sensor.initialize(self)

    def readTrim(self):
        block = self.readBlock(0x88, 24)

        self.trim["T1"] = block[1] * 256 + block[0]
        self.trim["T2"] = block[3] * 256 + block[2]
        if self.trim["T2"] > 32767:
            self.trim["T2"] -= 65536
        self.trim["T3"] = block[5] * 256 + block[4]
        if self.trim["T3"] > 32767:
            self.trim["T3"] -= 65536

        self.trim["P1"] = block[7] * 256 + block[6]
        self.trim["P2"] = block[9] * 256 + block[8]
        if self.trim["P2"] > 32767:
            self.trim["P2"] -= 65536
        self.trim["P3"] = block[11] * 256 + block[10]
        if self.trim["P3"] > 32767:
            self.trim["P3"] -= 65536
        self.trim["P4"] = block[13] * 256 + block[12]
        if self.trim["P4"] > 32767:
            self.trim["P4"] -= 65536
        self.trim["P5"] = block[15] * 256 + block[14]
        if self.trim["P5"] > 32767:
            self.trim["P5"] -= 65536
        self.trim["P6"] = block[17] * 256 + block[16]
        if self.trim["P6"] > 32767:
            self.trim["P6"] -= 65536
        self.trim["P7"] = block[19] * 256 + block[18]
        if self.trim["P7"] > 32767:
            self.trim["P7"] -= 65536
        self.trim["P8"] = block[21] * 256 + block[20]
        if self.trim["P8"] > 32767:
            self.trim["P8"] -= 65536
        self.trim["P9"] = block[23] * 256 + block[22]
        if self.trim["P9"] > 32767:
            self.trim["P9"] -= 65536

    def readData(self):
        currTime = int(round(time() * 1000))
        if self.lastRead + 1000 < currTime:
            print "Reading...\n"
            self.data = self.readBlock(0xF7, 8)
            adc_t = ((self.data[3] * 65536) + (self.data[4] * 256) + (self.data[5] & 0xF0)) / 16
            var1 = ((adc_t) / 16384.0 - (self.trim["T1"]) / 1024.0) * (self.trim["T2"])
            var2 = (((adc_t) / 131072.0 - (self.trim["T1"]) / 8192.0) * ((adc_t)/131072.0 - (self.trim["T1"])/8192.0)) * (self.trim["T3"])
            self.tFine = var1 + var2
            self.lastRead = currTime

class Thermostat(Pressure):
    def __init__(self, bus):
        Pressure.__init__(self, bus, "Thermostat")

    def readTemp(self):
        self.readData()
        cTemp = self.tFine / 5120.0
        return cTemp * 1.8 + 32

    def __str__(self):
        return "Temperature: %.2f F\n" % self.readTemp()

class Barometer(Pressure):
    def __init__(self, bus):
        Pressure.__init__(self, bus, "Barometer")

    def readPressure(self):
        self.readData()
        adc_p = ((self.data[0] * 65536) + (self.data[1] * 256) + (self.data[2] & 0xF0)) / 16

        var1 = (self.tFine / 2.0) - 64000.0
        var2 = var1 * var1 * (self.trim["P6"]) / 32768.0
        var2 = var2 + var1 * (self.trim["P5"]) * 2.0
        var2 = (var2 / 4.0) + ((self.trim["P4"]) * 65536.0)
        var1 = ((self.trim["P3"]) * var1 * var1 / 524288.0 + (self.trim["P2"]) * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * (self.trim["P1"])
        p = 1048576.0 - adc_p
        p = (p - (var2 / 4096.0)) * 6250.0 / var1
        var1 = (self.trim["P9"]) * p * p / 2147483648.0
        var2 = p * (self.trim["P8"]) / 32768.0
        return (p + (var1 + var2 + (self.trim["P7"])) / 16.0) / 100

    def __str__(self):
        return "Pressure: %.2f hPa\n" % self.readPressure()


class SensorError(Exception):
    def __init__(self, name):
        self.name = name