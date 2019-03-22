#!/usr/bin/env python3

"""
--------------------------------------------------------------------------------------
Created on  : 22 March 2019
Author      : Jusnaini
Descriptions
------------
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
--------------------------------------------------------------------------------------
"""
import serial
import sys

# Configure the serial port and open/activate it
ser = serial.Serial(
    port      = '/dev/ttyS7',
    baudrate  = 9600,
    parity    = serial.PARITY_NONE,
    stopbits  = serial.STOPBITS_ONE,
    bytesize  = serial.EIGHTBITS,
    timeout   = 1,
    xonxoff   = False,
    dsrdtr    = False,
    rtscts    = False,
    writeTimeout = None
)

def csum(data):
    checksum = 0
    for i in data:
        checksum = checksum ^ ord(i)
    #checksum = hex(checksum)[2:]
    print("Apprate with checksum = "+ (data+chr(checksum)))
    return(data+chr(checksum))

while True:
    try:
        in_Rate = input("Input rate : ") #raw_input accept string
        App_Rate = 'SD' + str(in_Rate)
        App_Rate = "{%s}" % (csum(App_Rate))
        ser.write(App_Rate.encode())

    except KeyboardInterrupt:
        print("KeyboardInterrupted")
        sys.exit(0)

ser.close()


