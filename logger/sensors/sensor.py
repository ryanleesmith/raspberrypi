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

class IMU(Sensor):
    def __init__(self, bus, address, id, name):
        Sensor.__init__(self, bus, address, id, name)

    def adjust(self, low, high):
        combined = (low | high <<8)
        return combined if combined < 32768 else combined - 65536

    def readRange(self, lpReg, hpReg):
        low = self.read(lpReg)
        high = self.read(hpReg)
        return self.adjust(low, high)

class Accelerometer(IMU):
    AXIS_ENABLE_REGISTER = 0x1F
    OUTPUT_CONFIG_REGISTER = 0x20

    X_LP_REGISTER = 0x28
    X_HP_REGISTER = 0x29
    Y_LP_REGISTER = 0x2A
    Y_HP_REGISTER = 0x2B
    Z_LP_REGISTER = 0x2C
    Z_HP_REGISTER = 0x2D

    def __init__(self, bus):
        IMU.__init__(self, bus, 0x6A, 0x68, "Accelerometer")

    def initialize(self):
        # Write axis enablement register
        # DEC(7-6) Z(5) Y(4) X(3) NON(2-0)
        self.write(Accelerometer.AXIS_ENABLE_REGISTER, 0b00111000)

        # Write output config register
        # ODR(7-5) FULLSCALE(4-3) BWTOGGLE(2) BWVAL(1-0) 
        self.write(Accelerometer.OUTPUT_CONFIG_REGISTER, 0b00100000)

    def readX(self):
        return self.readRange(Accelerometer.X_LP_REGISTER, Accelerometer.X_HP_REGISTER)

    def readY(self):
        return self.readRange(Accelerometer.Y_LP_REGISTER, Accelerometer.Y_HP_REGISTER)

    def readZ(self):
        return self.readRange(Accelerometer.Z_LP_REGISTER, Accelerometer.Z_HP_REGISTER)

    def __str__(self):
        return "Accel\tX: %.2f\t Y: %.2f\t Z: %.2f\n" % (self.readX(), self.readY(), self.readZ())

class Gyroscope(IMU):
    AXIS_ENABLE_REGISTER = 0x1E
    OUTPUT_CONFIG_REGISTER = 0x10
    ORIENTATION_REGISTER = 0x13

    X_LP_REGISTER = 0x18
    X_HP_REGISTER = 0x19
    Y_LP_REGISTER = 0x1A
    Y_HP_REGISTER = 0x1B
    Z_LP_REGISTER = 0x1C
    Z_HP_REGISTER = 0x1D

    def __init__(self, bus):
        IMU.__init__(self, bus, 0x6A, 0x68, "Gyroscope")

    def initialize(self):
        # Write axis enablement register
        # NON(7-6) Z(5) Y(4) X(3) NON(2) LIR(1) 4D(0)
        self.write(Gyroscope.AXIS_ENABLE_REGISTER, 0b00111000)

        # Write output config register
        # ODR(7-5) FULLSCALE(4-3) NON(2) BWVAL(1-0) 
        self.write(Gyroscope.OUTPUT_CONFIG_REGISTER, 0b10111000)

        # Write orientation register
        # NON(7-6) X(5) Y(4) Z(3) ORIENT(2-0)
        self.write(Gyroscope.ORIENTATION_REGISTER, 0b00111000)

    def readX(self):
        return self.readRange(Gyroscope.X_LP_REGISTER, Gyroscope.X_HP_REGISTER)

    def readY(self):
        return self.readRange(Gyroscope.Y_LP_REGISTER, Gyroscope.Y_HP_REGISTER)

    def readZ(self):
        return self.readRange(Gyroscope.Z_LP_REGISTER, Gyroscope.Z_HP_REGISTER)

    def __str__(self):
        return "Gyro\tX: %.2f\t Y: %.2f\t Z: %.2f\n" % (self.readX(), self.readY(), self.readZ())

class Magnetometer(IMU):
    def __init__(self, bus):
        IMU.__init__(self, bus, 0x1C, 0x3D, "Magnetometer")

class Pressure(Sensor):
    CTRL_MEAS_REGISTER = 0xF4
    CONFIG_REGISTER = 0xF5

    initialized = False
    trim = {}
    data = []
    fineTemperature = 0
    finePressure = 0
    lastRead = 0

    def __init__(self, bus, name):
        Sensor.__init__(self, bus, 0x77, 0x58, name)
        self.idRegister = 0xD0

    def initialize(self):
        if not Pressure.initialized:
            Pressure.initialized = True
            self.readTrim()
            # Write control measurement register
            # TEMP(7-5) PRES(4-2) MODE(1-0)
            # 0x27 = 001 001 11
            # 0x2F = 001 011 11
            # 0x4F = 010 011 11
            self.write(Pressure.CTRL_MEAS_REGISTER, 0x2F)
            # Write config register
            # STBY(7-5) FLTR(4-2) SPIW(0)
            # 0xA0 = 101 000 00
            # 0xB0 = 101 100 00
            self.write(Pressure.CONFIG_REGISTER, 0xB0)
        
        Sensor.initialize(self)

    def readTrim(self):
        block = self.readBlock(0x88, 24)

        Pressure.trim["T1"] = block[1] * 256 + block[0]
        Pressure.trim["T2"] = block[3] * 256 + block[2]
        if Pressure.trim["T2"] > 32767:
            Pressure.trim["T2"] -= 65536
        Pressure.trim["T3"] = block[5] * 256 + block[4]
        if Pressure.trim["T3"] > 32767:
            Pressure.trim["T3"] -= 65536

        Pressure.trim["P1"] = block[7] * 256 + block[6]
        Pressure.trim["P2"] = block[9] * 256 + block[8]
        if Pressure.trim["P2"] > 32767:
            Pressure.trim["P2"] -= 65536
        Pressure.trim["P3"] = block[11] * 256 + block[10]
        if Pressure.trim["P3"] > 32767:
            Pressure.trim["P3"] -= 65536
        Pressure.trim["P4"] = block[13] * 256 + block[12]
        if Pressure.trim["P4"] > 32767:
            Pressure.trim["P4"] -= 65536
        Pressure.trim["P5"] = block[15] * 256 + block[14]
        if Pressure.trim["P5"] > 32767:
            Pressure.trim["P5"] -= 65536
        Pressure.trim["P6"] = block[17] * 256 + block[16]
        if Pressure.trim["P6"] > 32767:
            Pressure.trim["P6"] -= 65536
        Pressure.trim["P7"] = block[19] * 256 + block[18]
        if Pressure.trim["P7"] > 32767:
            Pressure.trim["P7"] -= 65536
        Pressure.trim["P8"] = block[21] * 256 + block[20]
        if Pressure.trim["P8"] > 32767:
            Pressure.trim["P8"] -= 65536
        Pressure.trim["P9"] = block[23] * 256 + block[22]
        if Pressure.trim["P9"] > 32767:
            Pressure.trim["P9"] -= 65536

    def readData(self):
        currTime = int(round(time() * 1000))
        # BMP Sensor Standby set to 1000ms
        if Pressure.lastRead + 1000 < currTime:
            Pressure.data = self.readBlock(0xF7, 8)

            adc_t = ((Pressure.data[3] * 65536) + (Pressure.data[4] * 256) + (Pressure.data[5] & 0xF0)) / 16
            var1 = ((adc_t) / 16384.0 - (Pressure.trim["T1"]) / 1024.0) * (Pressure.trim["T2"])
            var2 = (((adc_t) / 131072.0 - (Pressure.trim["T1"]) / 8192.0) * ((adc_t)/131072.0 - (Pressure.trim["T1"])/8192.0)) * (Pressure.trim["T3"])
            Pressure.fineTemperature = var1 + var2

            adc_p = ((Pressure.data[0] * 65536) + (Pressure.data[1] * 256) + (Pressure.data[2] & 0xF0)) / 16
            var1 = (Pressure.fineTemperature / 2.0) - 64000.0
            var2 = var1 * var1 * (Pressure.trim["P6"]) / 32768.0
            var2 = var2 + var1 * (Pressure.trim["P5"]) * 2.0
            var2 = (var2 / 4.0) + ((Pressure.trim["P4"]) * 65536.0)
            var1 = ((Pressure.trim["P3"]) * var1 * var1 / 524288.0 + (Pressure.trim["P2"]) * var1) / 524288.0
            var1 = (1.0 + var1 / 32768.0) * (Pressure.trim["P1"])
            p = 1048576.0 - adc_p
            p = (p - (var2 / 4096.0)) * 6250.0 / var1
            var1 = (Pressure.trim["P9"]) * p * p / 2147483648.0
            var2 = p * (Pressure.trim["P8"]) / 32768.0
            Pressure.finePressure = p + (var1 + var2 + (Pressure.trim["P7"])) / 16.0

            Pressure.lastRead = currTime

class Thermometer(Pressure):
    def __init__(self, bus):
        Pressure.__init__(self, bus, "Thermometer")

    def readTemperature(self):
        self.readData()
        cTemp = Pressure.fineTemperature / 5120.0
        return cTemp * 1.8 + 32

    def __str__(self):
        return "Temperature: %.2f F\n" % self.readTemperature()

class Barometer(Pressure):
    def __init__(self, bus):
        Pressure.__init__(self, bus, "Barometer")

    def readPressure(self):
        self.readData()
        return Pressure.finePressure / 100

    def __str__(self):
        return "Pressure: %.2f hPa\n" % self.readPressure()

class Altimeter(Pressure):
    def __init__(self, bus):
        Pressure.__init__(self, bus, "Altimeter")

    def readAltitude(self):
        self.readData()
        cTemp = Pressure.fineTemperature / 5120.0
        hpaPres = Pressure.finePressure / 100
        mAlt = ((((1013.25 / hpaPres) ** (1 / 5.257)) - 1) * (cTemp + 273.15)) / 0.0065
        return mAlt * 3.281

    def __str__(self):
        return "Altitude: %.2f ft\n" % self.readAltitude()

class SensorError(Exception):
    def __init__(self, name):
        self.name = name