#!/usr/bin/env python

import socket
import sys

bufferSize    = 1024
serverAddressPort = ("127.0.0.1", 4445)

msgFromClient = "#,GStage,GPS1,GPS2,A,A,APPRATE" # 7strings
bytesToSend = str.encode(msgFromClient)

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

try:
    # Send to server using created UDP socket
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

    # Get data from server
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    msg = "Message from Server {}".format(msgFromServer[0])
    print(msg)
except KeyboardInterrupt:
    print("Client Keyboard Interrupted")
    sys.exit(0)


UDPClientSocket.close()