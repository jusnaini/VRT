#!/usr/bin/env python3

"""
--------------------------------------------------------------------------------------
Created on  : 20 March 2019
Author      : Jusnaini
Descriptions:
         Read data from CropCircle sensor
         Serial port command to display data on terminal:
                sudo chmod o+rw /dev/ttyS#
                sudo stty -F /dev/ttyS# 38400 raw -echo
                sudo cat /dev/ttyS#
--------------------------------------------------------------------------------------
"""

import serial
import sys

ser = serial.Serial(
    port      = '/dev/ttyS8',
    baudrate  = 38400,
    parity    = serial.PARITY_NONE,
    stopbits  = serial.STOPBITS_ONE,
    bytesize  = serial.EIGHTBITS,
    timeout   = 1,
    xonxoff   = False,
    dsrdtr    = False,
    rtscts    = False,
    writeTimeout = None
)

try:
    ser.open()
except Exception as e:
    print("Exception: Opening serial port: " + str(e))


while True:
    try:
        data = ser.readline().decode()
        print(data)

    except Exception as e:
        print ("Error communicating..: " + str(e))
    except KeyboardInterrupt:
        print("KeyboardInterrupted")
        sys.exit(0)

ser.close()

