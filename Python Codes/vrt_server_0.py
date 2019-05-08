#!/usr/bin/env python3

"""
--------------------------------------------------------------------------------------
Created on  : 29 April 2019
Author      : Jusnaini
Descriptions:
    1. Settings
        Crop Circle:
        Serial port command to display data on terminal:
            sudo chmod o+rw /dev/ttyS#
            sudo stty -F /dev/ttyS# 38400 raw -echo
            sudo cat /dev/ttyS#
         If permission denied, consider to change port mode to 777

        Bogballe Calibrator:
        Send command to change calibrator parameters value.
            Application rate - {SDXXXYY}
                XXX - value in 3 digits
                YY - checksum in char
            Debugging
            ---------
            WRITE terminal:
            $ sudo chmod o+rw /dev/ttyS9
            $ sudo echo -e "{124\x20} > /dev/ttyS9"
        READ terminal:
        $ sudo stty -F /dev/ttyS9 9600 raw -echo
        $ sudo cat /dev/ttyS9

    2. Procedure
    Get data from Crop Circle
    Calculate vegetation index derivatives
    Apply model
    Get prediction
    Set Bogballe applicator
--------------------------------------------------------------------------------------
"""

import serial
import sys
import datetime

# Configure and open the serial port
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
    while True:
        data = ser.readline().decode()
        print(str(datetime.datetime.now()) + "Crop Circle: {} ".format(data))
except KeyboardInterrupt:
    print ("KeyboardInterrupt")
    sys.exit()
ser.close()