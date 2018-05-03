""" 
@author: zoutai
@file: pngToGif.py 
@time: 2018/04/30 
@description: 
"""
import matplotlib.pyplot as plt
import imageio,os
images = []
filenames=sorted((fn for fn in os.listdir('.') if fn.endswith('.png')))
for filename in filenames:
    images.append(imageio.imread(filename))
imageio.mimsave('gif.gif', images,duration=1)