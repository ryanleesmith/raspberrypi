#!/usr/bin/python

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import time
import math
from imu import IMU
import datetime
import os

def loop():
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

IMU.detectImu()
IMU.init()

while True:
    loop()
    time.sleep(1)