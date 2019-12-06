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
                sudo chmod o+rw /dev/ttyS8
                sudo chmod o+rw /dev/ttyS7
                sudo stty -F /dev/ttyS8 38400 raw -echo
                sudo stty -F /dev/ttyS7 9600 raw -echo
                sudo cat /dev/ttyS8
         If permission denied, consider to change port mode to 777
--------------------------------------------------------------------------------------
"""

import socket
import serial
import sys
import random
import datetime,time
import pandas as pd
import numpy as np
import pickle
from collections import Counter

from utils import CropCircle, BogballeCalibrator
from utils import features,get_features,predModel,set_bogballe,get_model

print("===============================")
print("AN ON-THE-GO VRT CONTROL SYSTEM")
print("===============================")


# UDP socket configurations
UDP_IP     = "10.42.0.1"
UDP_PORT   = 4445
bufferSize = 1024

# Serial port configurations
ser_sensor = CropCircle()
ser_calibrator = BogballeCalibrator()

# User input
print('(1-25dat,2-50dat,3-70dat)')
i = input('Growth Stage : ')
model,crop_len= get_model(int(i))
get_filename = input('Filename     : ')

# Open file to log data
timestamp = time.strftime("%Y%m%d_%H%M%S")
f0 = open(get_filename+'_0_'+'.csv',"w+") # raw data
f1 = open(get_filename+'_1_'+'.csv',"w+") # convolved data in 1 s
f2 = open(get_filename+'_2_'+'.csv',"w+") # predicted data after 5s (1loop=1s)

#header0 = "Datetime,RedEdge,NIR,RED,NDRE,NDVI"
#header  = "Datetime,RedEdge,NIR,NDRE,RERVI,RERDVI,REDVI,RESAVI,MRESAVI,CI,N_pred,N_rate"

header0= "Datetime,RedEdge,NIR,Red,NDRE,NDVI"
header= "Datetime,RedEdge,NIR,NDVI,REDVI,RERDVI,RESAVI,N_pred,N_rate"

f0.write(header0+'\n')
f1.write(header+'\n')
f2.write(header+'\n')

# Set model based on growth stage
svm_model = pickle.load(open(model, 'rb'))

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)

# Bind address and ip
UDPServerSocket.bind((UDP_IP,UDP_PORT))
print("Waiting for request..\n")

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
            print("Paused...........")
            App_Rate    = 000
            Green_Index = 000
            Plant_Vol   = 000
            Sys_Volt    = 000
            GPS_x       = 000
            GPS_y       = 000
        else:
            if manual == 1:
                print("-------------")
                print("MODE : MANUAL")
                print("-------------")
                App_Rate    = int(strData[6])
                Green_Index = round(random.random(), 2)
                Plant_Vol   = round(random.uniform(10, 100), 2)
                Sys_Volt    = round(random.uniform(10, 12), 2)
                GPS_x       = strData[3]
                GPS_y       = strData[4]

            else:
                loop = 0
                status_count = Counter([])
                rate_count = Counter([])
                #crop_list = [[] for i in range(9)]
                crop_list = [[] for i in range(crop_len)]

                ## loop 5 times to select most frequent prediction
                while (loop in range(5)):
                    delay = 1
                    time_end = time.time() + delay
                    win_sz = 0

                    ## get data for every 1 s
                    while time.time() < time_end:
                        data = ser_sensor.readline().decode() # Read Crop Circle
                        msg = get_features(data)              # Compute other features
                        #print("{} : {}".format(datetime.datetime.now().isoformat(),data))
                        f0.write(datetime.datetime.now().isoformat() + '\t'+data+'\n')

                        for i, m in enumerate(msg):           # Append new data for each vi
                            crop_list[i].append(msg[i])
                        win_sz +=1                            # Count data len in 1s for moving average

                    crop_list_size = len(crop_list[0])        # track increasing  data len for 5s

                    # Print info
                    print("-----------")
                    print("MODE : AUTO")
                    print("-----------")
                    print("window_size = {}".format(str(win_sz)))
                    print("datalist_size = {}".format(str(crop_list_size)))

                    # Calculate moving average for every 1s
                    data_to_pred = list(map(lambda x: x[-1],[np.convolve(x, np.ones((win_sz,)) / win_sz, mode='valid') for x in crop_list]))
                    # Predict data for every 1s
                    N_rate, status = predModel(np.array(data_to_pred),svm_model)
                    # Update prediction counter
                    rate_count.update([N_rate])
                    status_count.update([status])

                    # Convert numpy.float64 to normal float to string for data logging. float64/float has no attribute write()
                    data_list = ",".join(map(str, np.array(data_to_pred).tolist()))
                    # write data of 1s
                    f1.write(datetime.datetime.now().isoformat() + '\t'+data_list+'\t' + status + '\t' + str(N_rate)+'\n')

                    # Round every sublist in list
                    # data_list = [np.round(float(data_list[i]),2) for i,m in enumerate(data_list)]
                    loop += 1

                App_Rate = rate_count.most_common(1)[0][0]      # select most frequent rate
                N_status = status_count.most_common(1)[0][0]    # select most frequent status
                Green_Index = 0.5
                Plant_Vol   = 777.7
                Sys_Volt    = 10
                GPS_x       = float(strData[4])
                GPS_y       = float(strData[4])

                ## log decision data into file
                f2.write(datetime.datetime.now().isoformat() + '\t' + data_list + '\t' + N_status + '\t' + str(App_Rate) + '\n')

        # send: "#,data1,data2,data3,data4,data5,data6"
        SendMsg2Client = "{},{},{},{},{},{},{}".format('#', App_Rate, Green_Index, Plant_Vol, Sys_Volt, GPS_x, GPS_y)
        print ('SendClientMessage: ' + SendMsg2Client)
        # UDPServerSocket.sendto(b'#,120,0.5,2.0,125.2,99,88', address)
        UDPServerSocket.sendto(str.encode(SendMsg2Client), address)

        # set Bogballe calibrator
        n = set_bogballe(App_Rate)
        ser_calibrator.write(n.encode())

    except KeyboardInterrupt:
        print("KeyboardInterrupted")
        sys.exit(0)

## close file as system exit
f0.close()
f1.close()
f2.close()

ser_sensor.close()
ser_calibrator.close()
UDPServerSocket.close()
