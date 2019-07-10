#!/usr/bin/python

import sys
import os
from os import path, system
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import time
from imu import IMU

def loop():
    system('clear')
    IMU.printData()
    return

def main():
    try:
        if IMU.detect():
            IMU.initialize()
            time.sleep(1)

            while True:
                loop()
                time.sleep(0.25)
    except KeyboardInterrupt:
        print("\nExiting...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

if __name__ == "__main__":
    main()