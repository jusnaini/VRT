#!/usr/bin/env python3

"""
--------------------------------------------------------------------------------------
Created on  : 20 March 2019
Author      : Jusnaini
Descriptions:
         Read data from CropCircle sensor
         Serial port command to display data on terminal:
                sudo chmod o+rw /dev/ttyS#
                sudo stty -F /dev/ttyS# 38400 raw -echo
                sudo cat /dev/ttyS#
         If permission denied, consider to change port mode to 777
--------------------------------------------------------------------------------------
"""
import serial
import sys
import datetime,time
import numpy as np
import pandas as pd
import random
import pickle
import csv
from collections import Counter
from utils import get_features, get_features, predModel

# Configure the serial port and open/activate it
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

# load svm model
mpath = '../svm_tuple.pkl'
svm_model, svm_Xtrain, svm_Ytrain, svm_score = pickle.load(open(mpath, 'rb'))




#"header = "Datetime,RedEdge,NIR,Red,NDRE,NDVI,RERVI,RERDVI,REDVI,RESAVI,MRESAVI,CI"


print ("Reading sensor..")
get_filename = input('Filename : ')
f = open(get_filename + '.csv', "w+")
try:

    loop = 0
    crop_list = [[] for i in range(9)]
    while (loop in range(5)):  # loop 5 times before determine predict
        delay = 1
        time_end = time.time() + delay
        win = 0

        while time.time() < time_end:
            data = ser.readline().decode()
            msg = get_features(data)
            #print(data)

            for i, m in enumerate(msg):
                crop_list[i].append(msg[i])
                # print("Crop_list : {}".format(crop_list))
            win += 1
            # print("======================================")
            # print("Crop_list2 : {}".format(crop_list))
            # print("======================================")

        win2 = len(crop_list[0])
        print("window_size = {}".format(str(win)))
        print("crop_list = {}".format(str(win2)))

        data_to_pred = list(map(lambda x: x[-1], [np.convolve(x, np.ones((3,)) / (3), mode='valid') for x in crop_list]))
        data_list = ",".join(map(str,np.array(data_to_pred).tolist()))
        N_rate, status = predModel(np.array(data_to_pred), svm_model)
        #data_list = [a, b, c,d,e,f,g,h,i]
        #print("a = {},b = {}, c = {}".format(a, b, c))
        #data_logged = ','.join(map(str, data_list))
        f.write(data_list + '\n')
        print(type(data_list))

        loop += 1




except Exception as e:
    print ("Error communicating..: " + str(e))
except KeyboardInterrupt:
    print("KeyboardInterrupted")
    sys.exit(0)
##f.close()
ser.close()


