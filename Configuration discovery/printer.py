import pickle
from recordclass import recordclass

Function = recordclass('Function', ['seq', 'short', 'long', 'value'])
VALUE = 120

with open('function.dat', 'rb') as infile:
	ledger = pickle.load(infile)
	
for record in ledger:
	if record.value > VALUE:
		print(record)