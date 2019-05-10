#!/usr/bin/env python3

"""
--------------------------------------------------------------------------------------
Created on  : 9 May 2019
Author      : Jusnaini
Descriptions:
    load svm_model
    using received serial data, predict the N status

--------------------------------------------------------------------------------------
"""
import socket
import sys
import random
import pickle
import numpy as np
import pandas as pd
from utils import get_features, predModel

localIP   = "127.0.0.1"
localPort =  4445
bufferSize = 1024

UDP_IP   = localIP
UDP_PORT = localPort

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)

# Bind address and ip
UDPServerSocket.bind((UDP_IP,UDP_PORT))

# load svm model
svm_model, svm_Xtrain, svm_Ytrain, svm_score = pickle.load(open("svm_tuple.pkl", 'rb'))

while (True):
    try:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]

        clientMsg = "Message from Client:{}".format(message)
        clientIP = "Client IP Address:{}".format(address)

        print(clientMsg)
        print(clientIP)

        data = get_features(message.decode())
        print(data)
        appRate = predModel(np.array(data),svm_model)

        MsgToClient = "{},{},{},{},{},{},{}".format('#', appRate, "Green_Index",
                                                "Plant_Vol", "Sys_Volt", "GPS_x", "GPS_y")
        UDPServerSocket.sendto(str.encode(MsgToClient), address)
        #UDPServerSocket.sendto(b'OK.Thank u.', address)
    except KeyboardInterrupt:
        print ("KeyboardInterrupted")
        sys.exit()
UDPServerSocket.close()
