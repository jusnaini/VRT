import pandas as pd
import numpy as np
import pickle

'''
def predModel(data):
    if(svm_model.predict([data]))== 0:
        print('Low')
    elif(svm_model.predict([data]))==1:
        print('Medium')
    elif(svm_model.predict([data]))== 2:
        print('High')
    else:
        print('Unknown')

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

    idx_list = [re,nir,ndre,rervi,rerdvi,redvi,resavi,mresavi,ci]
    #print(idx_list)
    return(idx_list)
'''

from utils import get_features, predModel
svm_model, svm_Xtrain, svm_Ytrain, svm_score = pickle.load(open("svm_tuple.pkl", 'rb'))

msgFromClient= "24.85835331,24.46869804,24.31803904,-0.008161426,0.005282896"
data = get_features(msgFromClient)
print(data)
a=20.7
b=32.7
c=0.22
d=1.576
e=1.63
f=11.94
g=0.33
h=0.36
i=0.57
predModel(np.array(data),svm_model)
#predModel(np.array([a,b,c,d,e,f,g,h,i]),svm_model)
