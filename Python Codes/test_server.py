#!/usr/bin/env python3

import socket
import sys
import random


def csum(data):
    checksum = 0
    for i in  range(len(data)):
        checksum = checksum ^ ord(data[i])
    #checksum = hex(checksum)[2:]
    checksum = chr(checksum)
    print("Apprate with checksum = "+ (data+checksum))
    #print("Apprate with checksum = %s" % (data + checksum))
    return(data+checksum)

def csum2(data):
    checksum = 0
    for i in data:
        checksum = checksum ^ ord(i)
    checksum = hex(checksum)[2:]
    print("Apprate with checksum = "+ (data+checksum))
    #print("Apprate with checksum = %s" % (data + checksum))
    return(data+checksum)

localIP   = "127.0.0.1"
localPort =  4445
bufferSize = 1024

#SENSORT_PORT
#CALIBRATOR_PORT

UDP_IP   = localIP
UDP_PORT = localPort

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)

# Bind address and ip
UDPServerSocket.bind((UDP_IP,UDP_PORT))

# Ready for incoming data
while (True):
    try:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]

        clientMsg = "Message from Client:{}".format(message)
        clientIP = "Client IP Address:{}".format(address)

        print(clientMsg)
        print(clientIP)

        #for strData in clientMsg.split(','):
        #    print("string data: " + strData)

        strData = message.decode().split(',')
        print("DataLen    : " + str(len(strData)))
        print("DataType   : " + str(type(strData)))
        print("Encoded    : " + str(strData)) #list has to be converted to str
        print("Formatted  : " + format(message))

        print ("------Data sent to client------")
        #App_Rate = 'SD124'
        App_Rate = input("Input rate : ") #raw_input accept string
        App_Rate = 'SD' + str(App_Rate)

        Green_Index = round(random.random(), 2)
        Plant_Vol = round(random.uniform(10, 100), 2)
        Sys_Volt = round(random.uniform(10, 12), 2)
        GPS_x = strData[2]
        GPS_y = strData[3]
        MsgToClient = "{},{},{},{},{},{},{}".format('#', csum(App_Rate), Green_Index,
                                                  Plant_Vol, Sys_Volt, GPS_x, GPS_y)
        UDPServerSocket.sendto(str.encode(MsgToClient), address)
        # UDPServerSocket.sendto(b'Data from server', address)

    except KeyboardInterrupt:
        print("KeyboardInterrupted")
        sys.exit(0)

UDPServerSocket.close()

"""
Strings are always Unicode:-
    - only accept byte-based to send and receive
    - str.encode(send_data) or b'message' convert string into binaries
    - format(message) decode into binary integer
    - message.decode() decode into binary character (normal string)
"""

