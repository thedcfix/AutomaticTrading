from random import randint
from functions import genExtractor, simulate
from recordclass import recordclass
import pickle
from multiprocessing import Process
import os
import time

Log = recordclass('Log', ['coin', 'value_ask', 'value_bid'])
Function = recordclass('Function', ['seq', 'short', 'long', 'value'])

# maximum sequence length
SEQ_LEN = 40
AVG_LEN = 1920
POINTS_PER_SEQ = 100
				
def run(seq):
	
	with open('log.dat', 'rb') as infile:
		ledger = pickle.load(infile)
		
	kmeans = genExtractor(seq, ledger)
	functionLog = []
		
	print("Thread " + str(seq) + " partito")
	
	for i in range(1, POINTS_PER_SEQ):
		short = randint(1, AVG_LEN)
		# forcing long != short
		long = short
		while (long == short):
			long = randint(1, AVG_LEN)

		value = simulate(seq, short, long, kmeans, ledger)
		print("Num: " + str(i) + "\t" + "Seq: " + str(seq) + "\t" + "Short: " + str(short) + "\t" + "Long: " + str(long) + "\t" + "Value: " + str(float("{0:.2f}".format(value))))
		
		# just keep configurations with value above 100
		if (value > 100):
			functionLog.append(Function(seq, short, long, value))
			
		with open('function' + str(seq) + '.dat', 'wb') as outfile:
			pickle.dump(functionLog, outfile)

# -------------------------------------------------------------------------------------------

if __name__ == '__main__':

	n_thread = 11;
	global_list = []
	processes = []
	
	# fisrt sequence length
	seq = 2
	last_index = seq;
	
	while seq <= SEQ_LEN:
	
		for p_number in range(n_thread):
			p = Process(target=run, args=(seq,))
			p.start()
			processes.append(p)
			seq += 1
		
		for p in processes:
			p.join()
		
		for num in range(n_thread):
			with open('function' + str(num + last_index) + '.dat', 'rb') as infile:
				ledger = pickle.load(infile)
			
			global_list = global_list + ledger
			os.remove('function' + str(num + last_index) + '.dat')
			
		last_index += n_thread
			
		with open('function.dat', 'wb') as outfile:
			pickle.dump(global_list, outfile)