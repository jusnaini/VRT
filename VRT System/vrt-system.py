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

Serial port setup:
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
import datetime
import pandas as pd
import numpy as np
import pickle
from utils import features,get_features,predModel,set_bogballe

# UDP socket configurations
UDP_IP     = "10.42.0.1"
UDP_PORT   = 4445
bufferSize = 1024

# Serial port configurations
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
# load svm model
mpath = '../svm_tuple.pkl'
svm_model, svm_Xtrain, svm_Ytrain, svm_score = pickle.load(open(mpath, 'rb'))

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)

# Bind address and ip
UDPServerSocket.bind((UDP_IP,UDP_PORT))
print("Waiting for request..\n")

## Open file to log data
get_filename = input('Filename : ')
f = open(get_filename+'.csv',"w+")
header = "Datetime,RedEdge,NIR,NDRE,RERVI,RERDVI,REDVI,RESAVI,MRESAVI,CI"
f.write(header+'\n')

while True:
    try:

        #get client information
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]
        '''

        print("SOURCE  : %s" % (address[0]))
        print("PORT    : %d" % (address[1]))
        print("MESSAGE : %s" % (message.decode()))
        '''
        strData = message.decode().split(',')

        '''
        print("start  : " + strData[0])
        print("pause  : " + strData[1])
        print("gstage : " + strData[2])
        print("gpsx   : " + strData[3])
        print("gpsy   : " + strData[4])
        print("manual : " + strData[5])
        print("apprate: " + strData[6])
        '''
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
                duration = 1
                time_start = datetime.datetime.now()
                time_end = time_start + datetime.timedelta(seconds=duration)
                crop_list = [[] for i in range(9)]
                total_data = 0

                while datetime.datetime.now() < time_end:
                    data = ser_sensor.readline().decode()
                    msg = get_features(data)
                    print(data)

                    for i, m in enumerate(msg):
                        crop_list[i].append(msg[i])
                    total_data += total_data+1

                a, b, c, d, e, f, g, h, i = (sum(l) / len(l) for l in crop_list)
                data_list = [a, b, c, d, e, f, g, h, i]
                print("total_data = {}".format(total_data))
                App_Rate,status = predModel(np.array(data_list), svm_model)
                Green_Index = 0.5
                Plant_Vol   = 777.7
                Sys_Volt    = 10
                GPS_x       = float(strData[4])
                GPS_y       = float(strData[4])

                ## log data into file
                log_data = ','.join(map(str,data_list))
                f.write(datetime.datetime.now().isoformat() + '\t' + log_data + status+'\n')

        # send: "#,data1,data2,data3,data4,data5,data6"
        clientMsg = "{},{},{},{},{},{},{}".format('#', App_Rate, Green_Index, Plant_Vol, Sys_Volt, GPS_x, GPS_y)
        print ('ClientMessage: ' + clientMsg)
        # UDPServerSocket.sendto(b'#,120,0.5,2.0,125.2,99,88', address)
        UDPServerSocket.sendto(str.encode(clientMsg), address)

        # set Bogballe calibrator
        n = set_bogballe(App_Rate)
        ser_calibrator.write(n.encode())

    except KeyboardInterrupt:
        print("KeyboardInterrupted")
        sys.exit(0)

    ## close file as system exit
    f.close()

ser_sensor.close()
ser_calibrator.close()
UDPServerSocket.close()
