#!/usr/bin/python

import sys
from os import path, system
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from imu import IMU

def loop():
    system('clear')
    IMU.printData()
    return

if IMU.detect():
    IMU.initialize()

    while True:
        loop()
        time.sleep(1)