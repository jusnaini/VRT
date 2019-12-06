import numpy as np
import pandas as pd
import serial

def CropCircle():
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
        writeTimeout = None )
    return ser_sensor

def BogballeCalibrator():
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
        writeTimeout = None )
    return ser_calibrator



## function to calculate checksum
def csum(data):
    checksum = 0
    for i in data:
        checksum = checksum ^ ord(i)
    print("Apprate with checksum = "+ (data+chr(checksum)))
    return(data+chr(checksum))

def set_bogballe(App_Rate):
    Nrate = 'SD' + '%03d'%App_Rate
    checksum = 0
    for i in Nrate:
        checksum = checksum ^ ord(i)
    #checksum = hex(checksum)[2:]
    N_apply = Nrate + chr(checksum)
    N_apply = "{%s}"%(N_apply)
    print("N to apply: {}".format(N_apply))
    return(N_apply)


## function to compute and return all features
def features(data):
    # unpack and split data into crop circle variables
    re,nir,red,ndre,ndvi = map(float,data.split(','))

    # derived other vegetation index
    rervi    = nir/re
    rerdvi   = (nir - re)/((nir+re)**0.5)
    redvi    = nir - re
    resavi   = (1.5)*((nir-re)/(nir+re+0.5))
    mresavi  = 0.5*(2*nir+1 - ((2*nir+1)**2 - 8*(nir-re))**0.5)
    ci       = nir/re - 1

    #idx_list1 = [re,nir,red,ndre,ndvi,rervi,rerdvi,redvi,resavi,mresavi,ci]
    idx_list1 = [re, nir, ndvi, redvi,rerdvi,  resavi]
    #print(idx_list)
    return(idx_list1)

## function to compute features for svm
def get_features(data):
    # unpack and split data into crop circle variables
    re,nir,red,ndre,ndvi = map(float,data.split(','))

    # derived other vegetation index
    rervi    = nir/re
    rerdvi   = (nir - re)/((nir+re)**0.5)
    redvi    = nir - re
    resavi   = (1.5)*((nir-re)/(nir+re+0.5))
    mresavi  = 0.5*(2*nir+1 - ((2*nir+1)**2 - 8*(nir-re))**0.5)
    ci       = nir/re - 1

    #idx_list1 = [re,nir,ndre,rervi,rerdvi,redvi,resavi,mresavi,ci]
    idx_list1 = [re,nir,ndvi,redvi,rerdvi,resavi]

    #print(idx_list)
    return(idx_list1)

def predModel(data,svm_model):
    if(svm_model.predict([data]))== 0:
        print('N_status : LOW')
        #N_recommend = 88 #5 dat
        N_recommend = 132 #25 dat
        #N_recommend = 151 #50 dat
        #N_recommend = 64 #70 dat
        status = 'low'

    elif(svm_model.predict([data]))==1:
        print('N_status : MEDIUM')
        #N_recommend = 53 #5 dat
        N_recommend = 79 #25 dat
        #N_recommend = 90 #50 dat
        #N_recommend = 40 #70 dat
        status = 'medium'

    elif(svm_model.predict([data]))== 2:
        print('N_status : HIGH')
        N_recommend = 0
        status = 'high'
    else:
        print('Unknown')
        N_recommend=0
        status = 'unknown'
    return [N_recommend, status]



def get_model(i):
    header0 = "Datetime,RedEdge,NIR,NDVI,REDVI,RERDVI,RESAVI"
    switcher={
        1:'model/dat25_model.pkl',
        2:'model/dat50_model.pkl',
        3:'model/dat70_model.pkl'
    }
    default = 'model/dat25_model.pkl'
    crop_len = 6
    print("Model loaded : {}".format(switcher.get(i)))
    return [switcher.get(i,default),crop_len]

# load svm model
#mpath = '../svm_tuple.pkl'
#svm_model, svm_Xtrain, svm_Ytrain, svm_score = pickle.load(open(mpath, 'rb'))

#mpath = 'model/dat25_model.pkl'
#svm_model = pickle.load(open(mpath, 'rb'))