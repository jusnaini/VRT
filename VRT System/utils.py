import numpy as np
import pandas as pd

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

    idx_list1 = [re,nir,red,ndre,ndvi,rervi,rerdvi,redvi,resavi,mresavi,ci]
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

    idx_list1 = [re,nir,ndre,rervi,rerdvi,redvi,resavi,mresavi,ci]
    #print(idx_list)
    return(idx_list1)

def predModel(data,svm_model):
    if(svm_model.predict([data]))== 0:
        print('N_status : LOW')
        N_recommend = 200
    elif(svm_model.predict([data]))==1:
        print('N_status : MEDIUM')
        N_recommend = 120
    elif(svm_model.predict([data]))== 2:
        print('N_status : HIGH')
        N_recommend = 200
    else:
        print('Unknown')
        N_recommend=0
    return(N_recommend)