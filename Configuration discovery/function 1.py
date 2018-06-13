from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from recordclass import recordclass
import pickle
import sys

Function = recordclass('Function', ['seq', 'short', 'long', 'value'])
seq = []
short = []
long = []
value = []

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

with open('function.dat', 'rb') as infile:
	function = pickle.load(infile)
	
for data in function:
	seq.append(data.seq)
	short.append(data.short)
	long.append(data.long)
	value.append(data.value)

seq = np.array(seq)
short = np.array(short)
long = np.array(long)
value = np.array(value)

ax.scatter(seq, short, value, c=value)
plt.show()