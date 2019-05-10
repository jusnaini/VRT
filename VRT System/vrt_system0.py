#!/usr/bin/env python3

"""
--------------------------------------------------------------------------------------
Created on  : 8 May 2019
Author      : Jusnaini
Descriptions:
         1. Read data from CropCircle sensor
         2. Compute features
         3. Calculate moving average for every 1 s, load model, n do prediction
         4. log predictions and select prediction with the most occurrences for every N times (e.g:5)
         5. set the application rate to Bogballe calibrator
         5. Send data to human-machine-interface (HMI) over UDP socket
--------------------------------------------------------------------------------------
"""

## load libraries
import socket
import serial
import sys
import time
import os
import pandas as pd
import numpy as np
import random
import pickle

from utils import csum, get_features, predModel

## function to calculate moving average

## UDP socket configurations
UDP_IP     = "10.42.0.1"
UDP_PORT   = 4445
bufferSize = 1024

## Serial port configurations
ser_sensor = serial.Serial(
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
ser_calibrator = serial.Serial(
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

## Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)

## Bind address and ip
UDPServerSocket.bind((UDP_IP,UDP_PORT))
print("Waiting for request..\n")

# load svm model
mpath = '../svm_tuple.pkl'
svm_model, svm_Xtrain, svm_Ytrain, svm_score = pickle.load(open(mpath, 'rb'))


## System Operation
while True:
    try:

        # get client information
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

        pause = int(strData[1])
        manual = int(strData[5])

        if pause == 1:
            App_Rate = 000
            #Green_Index = 000
            #Plant_Vol = 000
            #Sys_Volt = 000
            #GPS_x = 000
            #GPS_y = 000
        else:
            if manual == 1:
                App_Rate = int(strData[6])
                Green_Index = round(random.random(), 2)
                Plant_Vol = round(random.uniform(10, 100), 2)
                Sys_Volt = round(random.uniform(10, 12), 2)
                GPS_x = strData[3]
                GPS_y = strData[4]
            else:
                # Read Crop Circle sensor
                #data = ser_sensor.readline().decode().split(', ')
                data = ser_sensor.readline().decode()
                print("CropCircle: " + str(data))

                msg = get_features(data)
                App_Rate = predModel(msg,svm_model)
                Green_Index = float(data[1])
                Plant_Vol = float(data[2])
                Sys_Volt = float(data[3])
                GPS_x = float(data[4])
                GPS_y = float(strData[4])

        # send: "#,data1,data2,data3,data4,data5,data6"
        clientMsg = "{},{},{},{},{},{},{}".format('#', App_Rate, Green_Index, Plant_Vol, Sys_Volt, GPS_x, GPS_y)
        print('ClientMessage: ' + clientMsg)
        UDPServerSocket.sendto(str.encode(clientMsg), address)
    #try:
        in_Rate = input("Input rate : ") #raw_input accept string
        App_Rate = 'SD' + str(in_Rate)
        App_Rate = "{%s}" % (csum(App_Rate))
        ser_calibrator.write(App_Rate.encode())
    except KeyboardInterrupt:
        print("KeyboardInterrupted")
        sys.exit(0)
ser_sensor.close()
ser_calibrator.close()
UDPServerSocket.close()