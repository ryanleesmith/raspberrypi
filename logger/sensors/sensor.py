from time import time
import math
import datetime

def convert(bits, isUnsigned):
    combined = bits[0] | bits[1] << 8
    return combined if isUnsigned else (combined ^ 0x8000) - 0x8000

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
    AXIS_ENABLE_REGISTER = 0x1F
    OUTPUT_CONFIG_REGISTER = 0x20

    X_REGISTER = 0x28
    Y_REGISTER = 0x2A
    Z_REGISTER = 0x2C

    def __init__(self, bus):
        Sensor.__init__(self, bus, 0x6A, 0x68, "Accelerometer")

    def initialize(self):
        # Write axis enablement register
        # DEC(7-6) Z(5) Y(4) X(3) NON(2-0)
        self.write(Accelerometer.AXIS_ENABLE_REGISTER, 0b00111000)

        # Write output config register
        # ODR(7-5) FULLSCALE(4-3) BWTOGGLE(2) BWVAL(1-0)
        self.write(Accelerometer.OUTPUT_CONFIG_REGISTER, 0b00100000)

    def readX(self):
        return convert(self.readBlock(Accelerometer.X_REGISTER, 2), False)

    def readY(self):
        return convert(self.readBlock(Accelerometer.Y_REGISTER, 2), False)

    def readZ(self):
        return convert(self.readBlock(Accelerometer.Z_REGISTER, 2), False)

    def getNormalized(self):
        x = self.readX()
        y = self.readY()
        z = self.readZ()

        divisor = math.sqrt(x**2 + y**2 + z**2)
        xNorm = self.readX() / divisor
        yNorm = self.readY() / divisor

        return [xNorm, yNorm]

    def __str__(self):
        x = self.readX()
        y = self.readY()
        z = self.readZ()

        angleX = math.degrees(math.atan2(y, z))
        angleY = math.degrees(math.atan2(z, x) + math.pi)

        if angleY > 90:
            angleY -= 270.0
        else:
            angleY += 90.0

        output = "Accel Raw\tX: %.2f\t Y: %.2f\t Z: %.2f\n" % (x, y, z)
        output += "Accel Angle\tX: %.2f\t Y: %.2f\n" % (angleX, angleY)
        return output

class Gyroscope(Sensor):
    AXIS_ENABLE_REGISTER = 0x1E
    OUTPUT_CONFIG_REGISTER = 0x10
    ORIENTATION_REGISTER = 0x13

    X_REGISTER = 0x18
    Y_REGISTER = 0x1A
    Z_REGISTER = 0x1C

    GAIN = 0.070
    TIME = datetime.datetime.now()

    def __init__(self, bus):
        Sensor.__init__(self, bus, 0x6A, 0x68, "Gyroscope")

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
        return convert(self.readBlock(Gyroscope.X_REGISTER, 2), False)

    def readY(self):
        return convert(self.readBlock(Gyroscope.Y_REGISTER, 2), False)

    def readZ(self):
        return convert(self.readBlock(Gyroscope.Z_REGISTER, 2), False)

    def __str__(self):
        diff = datetime.datetime.now() - Gyroscope.TIME
        diff = diff.microseconds / (1000000 * 1.0)
        Gyroscope.TIME = datetime.datetime.now()

        x = self.readX()
        y = self.readY()
        z = self.readZ()

        rateX = x * Gyroscope.GAIN
        rateY = y * Gyroscope.GAIN
        rateZ = z * Gyroscope.GAIN

        angleX = rateX * diff
        angleY = rateY * diff
        angleZ = rateZ * diff

        output = "Gyro Raw\tX: %.2f\t Y: %.2f\t Z: %.2f\n" % (x, y, z)
        output += "Gyro Angle\tX: %.2f\t Y: %.2f\t Z: %.2f\n" % (angleX, angleY, angleZ)
        return output

class Magnetometer(Sensor):
    OUTPUT_CONFIG_REGISTER = 0x20
    SCALE_CONFIG_REGISTER = 0x21
    MODE_CONFIG_REGISTER = 0x22
    Z_MODE_CONFIG_REGISTER = 0x23

    X_REGISTER = 0x28
    Y_REGISTER = 0x2A
    Z_REGISTER = 0x2C

    def __init__(self, bus):
        Sensor.__init__(self, bus, 0x1C, 0x3D, "Magnetometer")

    def initialize(self):
        # Write x/y output config register
        # TEMPCOMP(7) MODE(6-5) ODR(4-2) FASTODR(1) TEST(0)
        self.write(Magnetometer.OUTPUT_CONFIG_REGISTER, 0b10111100)
        
        # Write scale config register
        # NON(7) FULLSCALE(6-5) NON(4) REBOOT(3) SOFTRESET(2) NON(1-0)
        self.write(Magnetometer.SCALE_CONFIG_REGISTER, 0b01000000)

        # Write system operating mode config register
        # NON(7-6) LOWPOWERMODE(5) NON(4-2) MODE(1-0)
        self.write(Magnetometer.MODE_CONFIG_REGISTER, 0b00000000)

        # Write z-axis operating mode config register
        # NON(7-4) Z-MODE(3-2) BLE(1) NON(0)
        self.write(Magnetometer.Z_MODE_CONFIG_REGISTER, 0b00000000)

    def readX(self):
        return convert(self.readBlock(Magnetometer.X_REGISTER, 2), False)

    def readY(self):
        return convert(self.readBlock(Magnetometer.Y_REGISTER, 2), False)

    def readZ(self):
        return convert(self.readBlock(Magnetometer.Z_REGISTER, 2), False)

    def __str__(self):
        return "Magnet Raw\tX: %.2f\t Y: %.2f\t Z: %.2f\n" % (self.readX(), self.readY(), self.readZ())

class IMU():
    DIRECTIONS = ["N", "NNE", "NE", "ENE",
                  "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW",
                  "W", "WNW", "NW", "NNW"]
    def __init__(self, bus):
        self.acc = Accelerometer(bus)
        self.gyr = Gyroscope(bus)
        self.mag = Magnetometer(bus)

    def detect(self):
        self.acc.detect()
        self.gyr.detect()
        self.mag.detect()

    def initialize(self):
        self.acc.initialize()
        self.gyr.initialize()
        self.mag.initialize()

    def getPitch(self):
        return math.asin(self.acc.getNormalized()[0])

    def getRoll(self):
        return -math.asin(self.acc.getNormalized()[1] / math.cos(self.getPitch()))

    def getHeading(self, compensated):
        magX = self.mag.readX()
        magY = self.mag.readY()

        if compensated:
            magZ = self.mag.readZ()
            pitch = self.getPitch()
            roll = self.getRoll()

            magX = magX * math.cos(pitch) + magZ * math.sin(pitch)
            magY = magX * math.sin(roll) * math.sin(pitch) + magY * math.cos(roll) + magZ * math.sin(roll) * math.cos(pitch)

        heading = 180 * math.atan2(magY, magX) / math.pi
        return heading if heading >= 0 else heading + 360

    def getDirection(self):
        heading = self.getHeading(True)
        return IMU.DIRECTIONS[round(heading / 22.5)]

    def __str__(self):
        output = str(self.acc) + "\n" + str(self.gyr) + "\n" + str(self.mag) + "\n"
        output += "Pitch: %.2f\n" % self.getPitch()
        output += "Roll: %.2f\n" % self.getRoll()
        output += "Heading: %.2f\n" % self.getHeading(False)
        output += "Compensated Heading: %.2f\n" % self.getHeading(True)
        output += "Direction: %s\n" % self.getDirection()
        return output

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

        Pressure.trim["T1"] = convert([block[0], block[1]], True)
        Pressure.trim["T2"] = convert([block[2], block[3]], False)
        Pressure.trim["T3"] = convert([block[4], block[5]], False)

        Pressure.trim["P1"] = convert([block[6], block[7]], True)
        Pressure.trim["P2"] = convert([block[8], block[9]], False)
        Pressure.trim["P3"] = convert([block[10], block[11]], False)
        Pressure.trim["P4"] = convert([block[12], block[13]], False)
        Pressure.trim["P5"] = convert([block[14], block[15]], False)
        Pressure.trim["P6"] = convert([block[16], block[17]], False)
        Pressure.trim["P7"] = convert([block[18], block[19]], False)
        Pressure.trim["P8"] = convert([block[20], block[21]], False)
        Pressure.trim["P9"] = convert([block[22], block[23]], False)

    def readData(self):
        currTime = int(round(time() * 1000))
        # BMP Sensor Standby set to 1000ms
        if Pressure.lastRead + 1000 < currTime:
            Pressure.data = self.readBlock(0xF7, 8)

            adc_t = ((Pressure.data[3] * 65536) + (Pressure.data[4] * 256) + (Pressure.data[5] & 0xF0)) / 16
            var1 = (adc_t / 16384.0 - Pressure.trim["T1"] / 1024.0) * Pressure.trim["T2"]
            var2 = ((adc_t / 131072.0 - Pressure.trim["T1"] / 8192.0) * (adc_t / 131072.0 - Pressure.trim["T1"] / 8192.0)) * Pressure.trim["T3"]
            Pressure.fineTemperature = var1 + var2

            adc_p = ((Pressure.data[0] * 65536) + (Pressure.data[1] * 256) + (Pressure.data[2] & 0xF0)) / 16
            var1 = (Pressure.fineTemperature / 2.0) - 64000.0
            var2 = var1 * var1 * Pressure.trim["P6"] / 32768.0
            var2 = var2 + var1 * Pressure.trim["P5"] * 2.0
            var2 = (var2 / 4.0) + (Pressure.trim["P4"] * 65536.0)
            var1 = (Pressure.trim["P3"] * var1 * var1 / 524288.0 + Pressure.trim["P2"] * var1) / 524288.0
            var1 = (1.0 + var1 / 32768.0) * Pressure.trim["P1"]
            p = 1048576.0 - adc_p
            p = (p - (var2 / 4096.0)) * 6250.0 / var1
            var1 = (Pressure.trim["P9"]) * p * p / 2147483648.0
            var2 = p * Pressure.trim["P8"] / 32768.0
            Pressure.finePressure = p + (var1 + var2 + Pressure.trim["P7"]) / 16.0

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