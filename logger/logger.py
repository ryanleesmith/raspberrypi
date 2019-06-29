#!/usr/bin/python

import time
import math
import IMU
import datetime
import os

IMU.detect()
IMU.init()

ACCx = IMU.readACCx()
ACCy = IMU.readACCy()
ACCz = IMU.readACCz()
GYRx = IMU.readGYRx()
GYRy = IMU.readGYRy()
GYRz = IMU.readGYRz()
MAGx = IMU.readMAGx()
MAGy = IMU.readMAGy()
MAGz = IMU.readMAGz()

print ("\nACCx %5.2f\tACCy %5.2f\tACCz %5.2f" % (ACCx, ACCy, ACCz))
print ("\nGYRx %5.2f\tGYRy %5.2f\tGYRz %5.2f" % (GYRx, GYRy, GYRz))
print ("\nMAGx %5.2f\tMAGy %5.2f\tMAGz %5.2f" % (MAGx, MAGy, MAGz))