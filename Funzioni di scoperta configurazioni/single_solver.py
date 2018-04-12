from random import randint
from functions import genExtractor, simulate
from recordclass import recordclass
import pickle
from multiprocessing import Process
import os
import time

Log = recordclass('Log', ['coin', 'value_ask', 'value_bid'])
Function = recordclass('Function', ['seq', 'short', 'long', 'value'])


AVG_LEN = 5000
POINTS_PER_SEQ = 100
				
def run(seq, id):
	
	with open('log.dat', 'rb') as infile:
                ledger = pickle.load(infile)
		
	kmeans = genExtractor(seq, ledger)
	functionLog = []
		
	print("Thread " + str(seq) + " partito")
	
	for i in range(1, POINTS_PER_SEQ):
		short = randint(675, 1400)
		# forzo il fatto che long sia diverso da short
		long = short
		while (long == short):
			long = randint(600, 800)

		value = simulate(seq, short, long, kmeans, ledger)
		print("Num: " + str(i) + "\t" + "Seq: " + str(seq) + "\t" + "Short: " + str(short) + "\t" + "Long: " + str(long) + "\t" + "Value: " + str(float("{0:.2f}".format(value))))
					
		functionLog.append(Function(seq, short, long, value))
			
		with open('function' + str(id) + '.dat', 'wb') as outfile:
			pickle.dump(functionLog, outfile)

# -------------------------------------------------------------------------------------------

if __name__ == '__main__':

	n_thread = 12;
	#modificare anche qui
	last_index = 25
	global_list = []
	processes = []
	
	seq = 25
	
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