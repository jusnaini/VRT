from collections import Counter
import numpy as np
import datetime
import time
import random



def most_frequent(List):
    occur_count = Counter(List)
    print(occur_count.most_common())
    return occur_count.most_common(1)[0][0]
'''
# Unit test

list = ['low','high','high','medium','medium','low']
print(most_frequent(list))

status = []
for i in range(5):
    x = input('status = ')
    status.append(x)

print("Thank you. The status is {} ".format(most_frequent(status)))
'''

def moving_average(data,win):
    return np.convolve(data,np.ones((win,))/win,mode='valid')

'''
# Unit test

list = [1,2,3,4,5,6,7,8]
print(moving_average(list,2))
'''

def moving_average2(a):
    ret = np.cumsum(a, dtype=float)
    ret[2:] = ret[2:] - ret[:-2]
    return ret[2-1:]/2
'''
# Unit test
list_2 = [[1,2,3],[4,5,6],[7,8,9]]
window = 2
a,b,c = [np.convolve(i,np.ones((window,))/window,mode='valid') for i in list_2]
print('a = {}, b = {}, c = {}'.format(a,b,c))
print("a = {}, b = {}, c = {} ".format(moving_average2(list_2[0]),
                                        moving_average2(list_2[1]),
                                        moving_average2(list_2[2])))
'''

def gen_data():
    #a,b,c,d,e,f,g,h,i = [round(random.random(),2) for i in range(9)]
    #return [round(random.random(),2) for i in range(9)]
    return [round(random.randint(0, 10), 2) for i in range(3)]
'''
data = gen_data()
print(data)
print(moving_average(data,3))
print(type(moving_average(data,3)))
'''

'''
duration = 1
time_start = datetime.datetime.now()
time_end = time_start + datetime.timedelta(seconds=duration)
crop_list = [[] for i in range(3)]
status_count = Counter([])
rate_count = Counter([])
loop = 0
#while datetime.datetime.now() < time_end:

delay=1    ###for 15 minutes delay
close_time=time.time()+delay



#while time.time() < close_time :
while loop in range(5) :
    data = gen_data()
    print("Data : {}".format(data))

    for i, m in enumerate(data):
        crop_list[i].append(data[i])
        print("Crop_list : {}".format(crop_list))
    print("======================================")
    print("Crop_list2 : {}".format(crop_list))
    print("======================================")
    #a, b, c, = [np.convolve(x, np.ones((3,)) / 3, mode='valid') for x in crop_list]
    #data_list = [a, b, c]
    loop += 1

a1,b1,c1 = [np.convolve(x, np.ones((3,)) / (3), mode='valid') for x in crop_list]
a, b, c, = map(lambda x: x[-1],[np.convolve(x, np.ones((3,)) / (3), mode='valid') for x in crop_list])

print("len = {}".format(str(len(crop_list[0]))))
print ("a1 = {},b1 = {}, c1 = {}".format(a1,b1,c1))
print("a = {},b = {}, c = {}".format(a, b, c))

win = len(crop_list[0])

# get the average over specify window
#a, b, c, = map(lambda x: x[-1],[np.convolve(x, np.ones((3,)) / (3), mode='valid') for x in crop_list])
#a1,b1,c1 = [np.convolve(x, np.ones((3,)) / (3), mode='valid') for x in crop_list]
#print ("a = {},b = {}, c = {}".format(a,b,c))
#print ("a1 = {},b1 = {}, c1 = {}".format(a1,b1,c1))
#data_list = [a,b,c]
#print("data list = {}".format(data_list))
#print("data type = {}".format(type(data_list)))
'''


loop = 0
crop_list = [[] for i in range(3)]

while (loop in range(5)):  # loop 5 times before determine predict
    delay = 1
    time_end = time.time() + delay
    win = 0

    while time.time() < time_end:
        data = gen_data()
        #print(data)

        for i, m in enumerate(data):
            crop_list[i].append(data[i])
            #print("Crop_list : {}".format(crop_list))
        win += 1
        #print("======================================")
        #print("Crop_list2 : {}".format(crop_list))
        #print("======================================")


    win2 = len(crop_list[0])
    print("window_size = {}".format(str(win)))
    print("crop_list = {}".format(str(win2)))

    a, b, c, = map(lambda x: x[-1], [np.convolve(x, np.ones((3,)) / (3), mode='valid') for x in crop_list])
    data_list = [a, b, c]
    print("a = {},b = {}, c = {}".format(a, b, c))

    loop += 1

