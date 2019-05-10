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
#from datetime import datetime
import datetime
import numpy as np
import pandas as pd
import random
import pickle

from utils import features, get_features, predModel

def average(crop_list):
    a, b, c, d, e, f, g, h, i, j, k = (sum(l) / len(l) for l in crop_list)
    data_list = "%.3f,%.3f,%.3f,%.3f,%.3f," \
                "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f" \
                % (a, b, c, d, e, f, g, h, i, j, k)
    return (data_list)

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


#get_filename = input('Filename : ')
#f = open(get_filename+'.csv',"w+")
header = "Datetime,RedEdge,NIR,Red,NDRE,NDVI,RERVI,RERDVI,REDVI,RESAVI,MRESAVI,CI"
if ser.isOpen():
    try:
        #f.write(header+'\n')

        while True:
            duration   = 1
            time_start = datetime.datetime.now()
            time_end   = time_start + datetime.timedelta(seconds=duration)
            crop_list  = [[] for i in range(9)]

            while datetime.datetime.now() < time_end:
                data = ser.readline().decode()
                msg  = get_features(data)

                #msg_pred = get_features(data)
                #App_rate = predModel(np.array(msg),svm_model)

                for i, m in enumerate(msg):
                    crop_list[i].append(msg[i])

            #data_list = average(crop_list)
            a, b, c, d, e, f, g, h, i = (sum(l) / len(l) for l in crop_list)
            #data_list = "%.3f,%.3f,%.3f,%.3f,%.3f," \
            #            "%.3f,%.3f,%.3f,%.3f" \
            #            % (a, b, c, d, e, f, g, h, i)

            data_list = [a,b,c,d,e,f,g,h,i]
            App_Rate = predModel(np.array(data_list),svm_model)
            print("Apprate = {}".format(App_Rate))
            print(type(msg))
            print(msg)
            print(data_list)
            #print (type(data_list))
            #print("CropCircle: {}" .format(features(data)))
            #f.write(datetime.datetime.now().isoformat() + '\t' + data_list + '\n')
            #print(datetime.datetime.now().isoformat() +'\t'+data_list+'\n')
            #print("Apprate = {}".format(App_rate))

    except Exception as e:
        print ("Error communicating..: " + str(e))
    except KeyboardInterrupt:
        print("KeyboardInterrupted")
        sys.exit(0)
    #f.close()
ser.close()


