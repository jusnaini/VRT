#!/usr/bin/env python

"""
--------------------------------------------------------------------------------------
Created on  : 9 May 2019
Author      : Jusnaini
Descriptions:
    send dummy data of CropCircle

--------------------------------------------------------------------------------------
"""

import socket
import sys
import random
import pandas as pd



bufferSize    = 1024
serverAddressPort = ("127.0.0.1", 4445)

msgFromClient= "24.85835331,24.46869804,24.31803904,-0.008161426,0.005282896"
#msgFromClient = "#,GStage,GPS1,GPS2,A,A,APPRATE" # 7strings
df = pd.read_csv('sample_data.csv',header=None,sep='\t',index_col=False,skiprows=1)

bytesToSend = str.encode(msgFromClient)

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#f = open('serverMsg.csv',"w+")
#get_filename = input('Filename : ')
#f = open(get_filename+'.csv',"w+")

try:
    while True:
        # Send to server using created UDP socket
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)

        # Get data from server
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        msg = "Message from Server {}".format(msgFromServer[0].decode())
        #f.write("{}\n".format(msgFromServer[0].decode()))
        print(msg)
except KeyboardInterrupt:
    print("Client Keyboard Interrupted")
    sys.exit(0)

#f.close()
UDPClientSocket.close()


