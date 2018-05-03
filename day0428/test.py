""" 
@author: zoutai
@file: test.py 
@time: 2018/05/01 
@description: 
"""
import numpy as np

# p1=[0.1,0.5]
# p2=[0.2,1.1]
p1 = [0.2, 0.5]
p2 = [0.2, 1.1]
ONE = 0.1
steps = int(max([abs(p2[0] - p1[0]), abs(p2[1] - p1[1])]) / ONE)
step1 = (max(p1[0], p2[0]) - min(p1[0], p2[0])) / steps
step1 = -step1 if p1[0] >= p2[0] else step1
step2 = (max(p1[1], p2[1]) - min(p1[1], p2[1])) / steps
step2 = -step2 if p1[1] >= p2[1] else step2

if p1[0] == p2[0]:
    y = np.arange(p1[1], p2[1], step2)
    x = []
    for j in range(len(y)):
        x.append(p1[0])
elif p1[1] == p2[1]:
    x = np.arange(p1[0], p2[0], step1)
    y = []
    for j in range(len(x)):
        y.append(p1[1])
else:
    for x1, y1 in zip(np.arange(p1[0], p2[0]), np.arange(p1[1], p2[1], step2)):
        x = x1
        y = y1
for i,j in zip(x,y):
    print(i,j)