from collections import Counter
import numpy as np

def most_frequent(List):
    occur_count = Counter(List)
    print(occur_count.most_common())
    return occur_count.most_common(1)[0][0]

#list = ['low','high','high','medium','medium','low']
#print(most_frequent(list))
'''
status = []
for i in range(5):
    x = input('status = ')
    status.append(x)

print("Thank you. The status is {} ".format(most_frequent(status)))
'''

def moving_average(data,win):
    return np.convolve(data,np.ones((win,))/win,mode='valid')

list = [1,2,3,4,5,6,7,8]
print(moving_average(list,2))

list_2 = [[1,2,3],[4,5,6],[7,8,9]]
window = 3
a,b,c = [np.convolve(i,np.ones((window,))/window,mode='valid') for i in list_2]
print('a = {}, b = {}, c = {}'.format(a,b,c))

def moving_average2(a):
    ret = np.cumsum(a, dtype=float)
    ret[2:] = ret[2:] - ret[:-2]
    return ret[2-1:]/2

print("a = {} ".format(moving_average2(list_2[0])))

t = 0
data = [1,2,3,4,5,6,7,8,9]
while t < 5:
    for i, m in enumerate(data):
        crop_list[i].append(data[i])

