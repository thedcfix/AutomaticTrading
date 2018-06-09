import pickle
from recordclass import recordclass
import sys
import numpy
from functions import genExtractor, getAvg, getFloatingAvg

Log = recordclass('Log', ['coin', 'value_ask', 'value_bid'])

# classes

class SuperQueue:
	def __init__(self, dim):
		self.items = []
		self.dim = dim
	
	def put(self, el):
		if len(self.items) == self.dim:
			self.items = self.items[1 :]
		self.items.append(el)
		
	def clear(self):
		del self.items[:]
		self.dim = 0
		
	def changeSize(self, dim):
		self.dim = dim
		
	def show(self):
		print(self.items)
		
# functions

def simulate(seq, short, long, kmeans, ledger):

	SEQ_SIZE = seq
	SHORT_AVG = short
	LONG_AVG = long
	
	BUDGET = 100
	INITIAL_BUDGET = BUDGET
	COINS = 0
	PROFIT = 0
	FEE = 0.26 / 100
	
	data_ask = []
	data_bid = []
	res = []
	queueShort = SuperQueue(SHORT_AVG)
	queueLong = SuperQueue(LONG_AVG)
	avg_short = []
	avg_long = []
	
	# fake values used just to iitialize the arrays
	GAIN = 20
	FLAT = 20
	LOSS = 20
	gain_array = []
	loss_array = []
	flat_array = []

	for log in ledger:
		if log.coin == "XRP":
			data_ask.append(log.value_ask)
			data_bid.append(log.value_bid)
			
	# creating the 3 arrays. One increasing, one decreasing and one stationary
	for i in range(SEQ_SIZE):
		gain_array.append(GAIN)
		loss_array.append(LOSS)
		flat_array.append(FLAT)
		
		GAIN = GAIN + GAIN * 0.01
		LOSS = LOSS - LOSS * 0.01
		
	# normalizing
	gain_array = gain_array / getAvg(numpy.array(gain_array))
	loss_array = loss_array / getAvg(numpy.array(loss_array))
	flat_array = flat_array / getAvg(numpy.array(flat_array))

	# getting the classes of the arrays (GAIN, LOSS e FLAT). They change with the sequence length
	GAIN = kmeans.predict([numpy.array(gain_array[:SEQ_SIZE])])[0]
	LOSS = kmeans.predict([numpy.array(loss_array[:SEQ_SIZE])])[0]
	FLAT = kmeans.predict([numpy.array(flat_array[:SEQ_SIZE])])[0]

	idx = 0
	daily_avg = []
	counter = 0
	days = 0
	sum = 0
	avg = 0
	# un record ogni 45 secondi per 24 ore
	DAILY_RECORDS = 24 * 3600 / 45
	avg_five = []
	avg_twenty = []
	els = SuperQueue(5)
	elss = SuperQueue(20)

	for i in range(len(data_ask) - 2):

		queueShort.put(data_ask[i])
		queueLong.put(data_ask[i])
		
		# floating average short period
		avg_short.append(getFloatingAvg(queueShort, SHORT_AVG))
		
		# floating average long period
		avg_long.append(getFloatingAvg(queueLong, LONG_AVG))

		if i > SEQ_SIZE - 1:
			array = numpy.array(data_ask[idx:i])
			array = array / getAvg(array)
			array = array**(1/2)
			res = kmeans.predict([array])[0]
			
			print(str(i) + "\t" + str(data_ask[i]) + "\t\t Trend: " + str(res) + "\t BUDGET: " + str(float("{0:.2f}".format(BUDGET))) + "\t" + str("up" if avg_short[-1] > avg_long[-1] else "down") 
					+ "\t PROFIT: " + str(float("{0:.4f}".format(PROFIT))))
			
			if res == GAIN and avg_short[-1] > avg_long[-1] and (len(avg_five) > 0 and  len(avg_twenty) > 0):
				# buying
				if COINS == 0 and avg_five[-1] > avg_twenty[-1]:
					num_coins = int((BUDGET - BUDGET * FEE) / data_ask[i] - 0.5)
					BUDGET = BUDGET - num_coins * (data_ask[i] + data_ask[i + 1]) / 2 - (data_ask[i] + data_ask[i + 1]) / 2 * FEE
					COINS = num_coins
			
			elif res == LOSS and avg_short[-1] < avg_long[-1]:				
				# slling
				if COINS > 0:
					BUDGET = BUDGET + COINS * (data_bid[i] + data_bid[i + 1]) / 2 - COINS * (data_bid[i] + data_bid[i + 1]) / 2 * FEE
					if BUDGET > INITIAL_BUDGET:
						diff = BUDGET - INITIAL_BUDGET
						PROFIT = PROFIT + BUDGET - INITIAL_BUDGET
						BUDGET = BUDGET - diff
					COINS = 0
			
			idx = idx + 1
			
		sum += data_ask[i]
		counter += 1
		avg = sum / counter
		
		if (counter == DAILY_RECORDS):
			sum /= DAILY_RECORDS
			daily_avg.append(sum)
			sum = 0
			counter = 0
			
			for av in daily_avg:
				els.put(av)
				elss.put(av)
			avg_five.append(getFloatingAvg(els, 5))
			avg_twenty.append(getFloatingAvg(elss, 20))
	
	print("\n\nIl budget finale è: " + str(BUDGET) + " con " + str(COINS) + " monete")
	print("Budget normalizzato: " + str(BUDGET + COINS * data_bid[-1]))
	print("Profitto: " + str(PROFIT))
	print("GAIN, LOSS & FLAT: " + str(GAIN) + " " + str(LOSS) + " " + str(FLAT))

SEQ_SIZE = int(sys.argv[1])
SHORT = int(sys.argv[2])
LONG = int(sys.argv[3])

with open('log_completo.dat', 'rb') as infile:
	ledger = pickle.load(infile)

kmeans = genExtractor(SEQ_SIZE, ledger)
simulate(SEQ_SIZE, SHORT, LONG, kmeans, ledger)