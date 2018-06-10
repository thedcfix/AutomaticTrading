import pickle
from recordclass import recordclass
import sys
import numpy
from functions import genExtractor, getAvg, getFloatingAvg, SuperQueue, simulate

Log = recordclass('Log', ['coin', 'value_ask', 'value_bid'])

SEQ_SIZE = int(sys.argv[1])
SHORT = int(sys.argv[2])
LONG = int(sys.argv[3])

with open('log.dat', 'rb') as infile:
	ledger = pickle.load(infile)

kmeans = genExtractor(SEQ_SIZE, ledger)
value, history, coins = simulate(SEQ_SIZE, SHORT, LONG, kmeans, ledger, 1)

# printing statistics. 100 is the initial budget used for the simulation
print("\n\nFinal budget: " + str(float("{0:.4f}".format((value)))) + " with " + str(coins) + " coins. The final budget accounts for those coins as sold.")
print("Profit: " + str(float("{0:.4f}".format((value - 100)))))
	
with open('history', 'wb') as outfile:
    pickle.dump(history, outfile)