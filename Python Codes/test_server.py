#!/usr/bin/env python3

import socket
import sys

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

        for strData in clientMsg.split(','):
            print("string data: " + strData)

        strData = message.decode().split(',')
        print("String data len: " + str(len(strData)))
        print("String data type: " + str(type(strData)))
        print(strData)
        print(format(message))

        print("Data1: " + strData[0])
        print("Data2: " + strData[1])
        print("Data3: " + strData[2])
        print("Data4: " + strData[3])
        print("Data5: " + strData[4])
        print("Data6: " + strData[5])
        print("Data7: " + strData[6])

        UDPServerSocket.sendto(b'Data from server', address)

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
