#!/usr/bin/env python3

"""
--------------------------------------------------------------------------------------
Created on  : 20 March 2019
Author      : Jusnaini
Descriptions:
         Read data from CropCircle sensor
         Send data to human-machine-interface (HMI) over UDP socket
         Serial port command to display data on terminal:
                sudo chmod o+rw /dev/ttyS#
                sudo stty -F /dev/ttyS# 38400 raw -echo
                sudo cat /dev/ttyS#
         If permission denied, consider to change port mode to 777
--------------------------------------------------------------------------------------
"""

import socket
import serial
import sys
import random

# UDP socket configurations
UDP_IP     = "10.42.0.1"
UDP_PORT   = 4445
bufferSize = 1024

# Serial port configurations
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

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)

# Bind address and ip
UDPServerSocket.bind((UDP_IP,UDP_PORT))
print("Waiting for request..\n")

# Open serial port
#ser.open()

while True:
    try:

        #get client information
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]

        print("SOURCE  : %s" % (address[0]))
        print("PORT    : %d" % (address[1]))
        print("MESSAGE : %s" % (message.decode()))

     52

        print("start  : " + strData[0])
        print("pause  : " + strData[1])
        print("gstage : " + strData[2])
        print("gpsx   : " + strData[3])
        print("gpsy   : " + strData[4])
        print("manual : " + strData[5])
        print("apprate: " + strData[6])

        pause = int(strData[1])
        manual = int(strData[5])

        if pause == 1:
            App_Rate    = 000
            Green_Index = 000
            Plant_Vol   = 000
            Sys_Volt    = 000
            GPS_x       = 000
            GPS_y       = 000
        else:
            if manual == 1:
                App_Rate    = int(strData[6])
                Green_Index = round(random.random(), 2)
                Plant_Vol   = round(random.uniform(10, 100), 2)
                Sys_Volt    = round(random.uniform(10, 12), 2)
                GPS_x       = strData[3]
                GPS_y       = strData[4]
            else:
                data = ser.readline().decode().split(', ')
                print("CropCircle: " + str(data))
                #App_Rate = random.choice([0, 50, 100, 150, 200])
                App_Rate    = float(data[0])
                Green_Index = float(data[1])
                Plant_Vol   = float(data[2])
                Sys_Volt    = float(data[3])
                GPS_x       = float(data[4])
                GPS_y       = float(strData[4])
        `1
        `+*+

        # send: "#,data1,data2,data3,data4,data5,data6"
        clientMsg = "{},{},{},{},{},{},{}".format('#', App_Rate, Green_Index, Plant_Vol, Sys_Volt, GPS_x, GPS_y)
        print ('ClientMessage: ' + clientMsg)
        # UDPServerSocket.sendto(b'#,120,0.5,2.0,125.2,99,88', address)
        UDPServerSocket.sendto(str.encode(clientMsg), address)

    except KeyboardInterrupt:
        print("KeyboardInterrupted")
        sys.exit(0)


ser.close()
UDPServerSocket.close()
