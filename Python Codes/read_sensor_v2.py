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


def vegetation_index(data):
    # unpack and split data into crop circle variables
    re,nir,red,ndre,ndvi = map(float,data.split(','))

    # derived other vegetation index
    rervi    = nir/re
    rerdvi   = (nir - re)/((nir+re)**0.5)
    redvi    = nir - re
    resavi   = (1/5)*((nir-re)/(nir+re+0.5))
    mresavi  = 0.5*(2*nir+1 - ((2*nir+1)**2 - 8*(nir-re))**0.5)
    ci       = nir/re - 1

    idx_list1 = [re,nir,red,ndre,ndvi,rervi,rerdvi,redvi,resavi,mresavi,ci]
    idx_list = "%.3f,%.3f,%.3f,%.3f,%.3f," \
               "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f" \
               % (re,nir,red,ndre,ndvi,rervi,rerdvi,redvi,resavi,mresavi,ci)
    #print(*idx_list1,sep=',\t')
    #print(idx_list)
    return(idx_list1)

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

get_filename = input('Filename : ')
f = open(get_filename+'.csv',"w+")
header = "Datetime,RedEdge,NIR,Red,NDRE,NDVI,RERVI,RERDVI,REDVI,RESAVI,MRESAVI,CI"
if ser.isOpen():
    try:
        f.write(header+'\n')

        while True:
            duration   = 1
            time_start = datetime.datetime.now()
            time_end   = time_start + datetime.timedelta(seconds=duration)
            crop_list  = [[] for i in range(11)]

            while datetime.datetime.now() < time_end:
                data = ser.readline().decode()
                msg  = vegetation_index(data)

                for i, m in enumerate(msg):
                   crop_list[i].append(msg[i])

            #a,b,c,d,e,f,g,h,i,j,k = (sum(l)/len(l) for l in crop_list)
            #data_list = "%.3f,%.3f,%.3f,%.3f,%.3f," \
            #           "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f" \
            #           % (a,b,c,d,e,f,g,h,i,j,k)
            data_list = average(crop_list)

            print(type(data_list))
            f.write(datetime.datetime.now().isoformat() + '\t' + data_list + '\n')
            print(datetime.datetime.now().isoformat() +'\t'+data_list+'\n')

    except Exception as e:
        print ("Error communicating..: " + str(e))
    except KeyboardInterrupt:
        print("KeyboardInterrupted")
        sys.exit(0)
    f.close()
ser.close()


