#!/usr/bin/env python3

"""
--------------------------------------------------------------------------------------
Created on  : 19 March 2019
Author      : Jusnaini
Descriptions:
          No hardware required
          To test if HMI receiver (tab) is able to correctly display data
--------------------------------------------------------------------------------------
"""

import socket
import sys
import random

ServerIP    = "192.168.43.107"
ServerPort  =  4445
bufferSize = 1024

UDP_IP   = ServerIP
UDP_PORT = ServerPort

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)

# Bind address and ip
UDPServerSocket.bind((UDP_IP,UDP_PORT))
print("Waiting for request..\n")

# Server
while (True):
    try:

        #recv: "start,pause,gstage,gpsx,gpsy,manual,apprate"
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]

        print("SOURCE  : %s" % (address[0]))
        print("PORT    : %d" % (address[1]))
        print("MESSAGE : %s" % (message.decode()))

        strData = message.decode().split(',')

        print("start  : " + strData[0])
        print("pause  : " + strData[1])
        print("gstage : " + strData[2])
        print("gpsx   : " + strData[3])
        print("gpsy   : " + strData[4])
        print("manual : " + strData[5])
        print("apprate: " + strData[6])

        pause  = int(strData[1])
        manual = int(strData[5])

        if pause == 1:
            App_Rate = 888
        else :
            if manual == 1:
                App_Rate = int(strData[6])
            else:
                App_Rate = random.choice([0, 50, 100, 150, 200])

        Green_Index = round(random.random(), 2)
        Plant_Vol   = round(random.uniform(10,100), 2)
        Sys_Volt    = round(random.uniform(10,12), 2)
        GPS_x       = strData[3]
        GPS_y       = strData[3]

        # send: "#,data1,data2,data3,data4,data5,data6"
        clientMsg = "{},{},{},{},{},{},{}".format('#',App_Rate,Green_Index,Plant_Vol,Sys_Volt,GPS_x,GPS_y)

        #UDPServerSocket.sendto(b'#,120,0.5,2.0,125.2,99,88', address)
        UDPServerSocket.sendto(str.encode(clientMsg), address)

    except KeyboardInterrupt:
        print("KeyboardInterrupted")
        sys.exit(0)

UDPServerSocket.close()


