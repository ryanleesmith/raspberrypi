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