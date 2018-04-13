from functions import simulate, genExtractor
from recordclass import recordclass
import pickle
from multiprocessing import Process

# used to test the best configuration to see if they are valid also on the long period

Log = recordclass('Log', ['coin', 'value_ask', 'value_bid'])
Function = recordclass('Function', ['seq', 'short', 'long', 'value'])

def run(config, ledger, i, best):
	print("Test configurazione " + str(i) + ": " + str(config))
	kmeans = genExtractor(config.seq, ledger)
	res = simulate(config.seq, config.short, config.long, kmeans, ledger)
	
	# keeping just the configurations with a value > 100
	if (res > 100):
		best.append(config)
		print("\t ------> Configurazione ottima: " + str(config) + " value: " + str(res))
		
if __name__ == '__main__':

	values = []
	ledger = []
	best = []
	training = []
	processes = []

	with open('function.dat', 'rb') as infile:
		values = pickle.load(infile)
		
	with open('log.dat', 'rb') as infile:
		training = pickle.load(infile)
		
	with open('log_completo.dat', 'rb') as infile:
		ledger = pickle.load(infile)
		
	print(str(len(values)) + " configurazioni trovate")

	# max number of threads
	max = 11
	dim = len(values)
	
	i = 0
	
	while i < dim:
	
		if ((dim - i) < max):
			max = dim - i
		
		for p_number in range(max):
			p = Process(target=run, args=(values[i], ledger, i, best))
			p.start()
			processes.append(p)
			i += 1
		
		for p in processes:
			p.join()