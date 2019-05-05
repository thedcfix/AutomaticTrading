from random import randint
from functions import genExtractor, simulate
from recordclass import recordclass
import pickle
from multiprocessing import Process
import os
import time
from datetime import timedelta
import gzip
import telepot

User = recordclass("User", ['id', 'wallet'])
Coin = recordclass("Coin", ['name', 'amount', 'investment', 'fee', 'last_ask', 'last_bid'])
Quotation = recordclass("Quotation", ['ask', 'bid'])
Log = recordclass('Log', ['coin', 'value_ask', 'value_bid'])
Function = recordclass('Function', ['seq', 'short', 'long', 'value'])

# maximum sequence length
SEQ_LEN = 120
AVG_LEN = 1920
POINTS_PER_SEQ = 100
				
def run(seq):
	
	with open('log.dat', 'rb') as infile:
		ledger = pickle.load(infile)
		
	kmeans = genExtractor(seq, ledger)
	functionLog = []
	
	print("Partita l'analisi per la sequenza", seq)
	
	for i in range(1, POINTS_PER_SEQ):
		short = randint(1, AVG_LEN)
		
		#forcing long > short
		long = randint(short+1, AVG_LEN+1)

		value = simulate(seq, short, long, kmeans, ledger, 0)
		print("Num: " + str(i) + "\t" + "Seq: " + str(seq) + "\t" + "Short: " + str(short) + "\t" + "Long: " + str(long) + "\t" + "Value: " + str(float("{0:.2f}".format(value))))
		
		# just keep configurations with value above X
		if (value > 100):
			functionLog.append(Function(seq, short, long, value))
			
		with open('function' + str(seq) + '.dat', 'wb') as outfile:
			pickle.dump(functionLog, outfile)

# -------------------------------------------------------------------------------------------

if __name__ == '__main__':

	n_thread = 1;
	global_list = []
	processes = []
	
	# fisrt sequence length
	seq = 22
	last_index = seq;
	
	while seq <= SEQ_LEN:
		
		start = time.time()
		
		run(seq)
		
		end = time.time()
		print(str(timedelta(seconds=end-start)))
		
		seq +=1
		
		for num in range(n_thread):
			with open('function' + str(num + last_index) + '.dat', 'rb') as infile:
				ledger = pickle.load(infile)
			
			global_list = global_list + ledger
			os.remove('function' + str(num + last_index) + '.dat')
			
		last_index += n_thread
			
		with open('function.dat', 'wb') as outfile:
			pickle.dump(global_list, outfile)
			
	with open('function.dat', 'rb') as infile:
		configFile = gzip.open("config","rb")
		config = pickle.load(configFile)
		configFile.close()
		
		bot = telepot.Bot("467920869:AAF9JHOTFqOyCzyHa8yQ-DYRT9sQvztyfSg")
		bot.sendDocument(config.id, infile)