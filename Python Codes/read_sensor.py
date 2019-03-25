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
         If permission denied, consider to change port mode to 777
--------------------------------------------------------------------------------------
"""
import serial
import sys

# Configure the serial port and open/activate it
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

# This is optional .
# Without 'try' will give error - try to open the opened port
'''
try:
    ser.open()
except Exception as e:
    print("Exception: Opening serial port: " + str(e))
'''
# This loop continuously read serial data until Keyboard interrupt
get_filename = input('Filename : ')
f = open(get_filename+'.csv',"w+")
header = "RedEdge,NIR,Red,NDRE,NDVI"
if ser.isOpen():
    try:
        f.write(header+'\n')
        while True:
            data = ser.readline().decode()
            print(data)
            f.write(data+'\n')

    except Exception as e:
        print ("Error communicating..: " + str(e))
    except KeyboardInterrupt:
        print("KeyboardInterrupted")
        sys.exit(0)
    f.close()
ser.close()

