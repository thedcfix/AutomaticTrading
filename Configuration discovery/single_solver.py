from random import randint
from functions import genExtractor, simulate
from recordclass import recordclass
import pickle
from multiprocessing import Process
import os
import time

Log = recordclass('Log', ['coin', 'value_ask', 'value_bid'])
Function = recordclass('Function', ['seq', 'short', 'long', 'value'])

# script used to discover in detail how a fixed sequence length evolves on the basis of the other two parameters

AVG_LEN = 5000
POINTS_PER_SEQ = 50
				
def run(seq, id):
	
	with open('log.dat', 'rb') as infile:
		ledger = pickle.load(infile)
		
	kmeans = genExtractor(seq, ledger)
	functionLog = []
		
	print("Thread " + str(seq) + " partito")
	
	for i in range(1, POINTS_PER_SEQ):
		# modify values. INSERT HERE !!!!!!
		short = randint(675, 1400)
		long = short
		while (long == short):
			# modify values. INSERT HERE !!!!!!
			long = randint(600, 800)

		value = simulate(seq, short, long, kmeans, ledger, 0)
		print("Num: " + str(i) + "\t" + "Seq: " + str(seq) + "\t" + "Short: " + str(short) + "\t" + "Long: " + str(long) + "\t" + "Value: " + str(float("{0:.2f}".format(value))))
					
		functionLog.append(Function(seq, short, long, value))
			
		with open('function' + str(id) + '.dat', 'wb') as outfile:
			pickle.dump(functionLog, outfile)

# -------------------------------------------------------------------------------------------

if __name__ == '__main__':

	n_thread = 11;
	global_list = []
	processes = []
	
	# insert sequence to inspect HERE !!!!!!
	seq = 25
	last_index = seq
	
	for p_number in range(n_thread):
		p = Process(target=run, args=(seq, p_number))
		p.start()
		processes.append(p)
		
	for p in processes:
		p.join()
	
	for num in range(n_thread):
		with open('function' + str(num) + '.dat', 'rb') as infile:
			ledger = pickle.load(infile)
		
		global_list = global_list + ledger
		os.remove('function' + str(num) + '.dat')
		
	last_index += n_thread
		
	with open('function.dat', 'wb') as outfile:
		pickle.dump(global_list, outfile)