from recordclass import recordclass
import pickle
import json
import time

Log = recordclass('Log', ['coin', 'value_ask', 'value_bid'])
Function = recordclass('Function', ['seq', 'short', 'long', 'value'])

with open('function.dat', 'rb') as infile:
	function = pickle.load(infile)

list = []

for point in function:
	tuple = (point[0], point[1], point[2], point[3])
	list.append(tuple)

with open('function.json', 'w') as outfile:
	json.dump(list, outfile)