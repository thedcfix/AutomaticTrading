import numpy
from sklearn.cluster import KMeans
from recordclass import recordclass
import pickle

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

def getAvg(array):
	sum = 0
	
	for el in array:
		sum = sum + el
		
	return sum / len(array)
	
def getFloatingAvg(queue, len):
	fibo = 0
	sum = 0
	size = len
		
	for k in queue.items:
		fibo += size
		sum += size * k
		size -= 1
		
	return (sum / fibo)
	
def genExtractor(seq, ledger):
	
	SEQ_SIZE = seq
		
	data = []
	samples = []

	for log in ledger:
		if log.coin == "XRP":
			data.append(log.value_ask)
		
	for i in range(len(data) - SEQ_SIZE):
		array = numpy.array(data[i : i + SEQ_SIZE])
		avg = getAvg(array)
		array = array / avg
		array = array**(1/2)
		samples.append(array)
	
	samples = numpy.array(samples)

	kmeans = KMeans(n_clusters=3, random_state=0).fit(samples)

	return kmeans
	
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
	
	#valori fittizi, servono solo per l'inizializzazione degli array
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
			
	# creo i 3 array per determinare dinamicamente (poi) i valori di GAIN, LOSS e FLAT
	for i in range(SEQ_SIZE):
		gain_array.append(GAIN)
		loss_array.append(LOSS)
		flat_array.append(FLAT)
		
		GAIN = GAIN + GAIN * 0.01
		LOSS = LOSS - LOSS * 0.01
		
	# normalizzo
	gain_array = gain_array / getAvg(numpy.array(gain_array))
	loss_array = loss_array / getAvg(numpy.array(loss_array))
	flat_array = flat_array / getAvg(numpy.array(flat_array))

	# determino le classi di appartenenza (GAIN, LOSS e FLAT)
	GAIN = kmeans.predict([numpy.array(gain_array[:SEQ_SIZE])])[0]
	LOSS = kmeans.predict([numpy.array(loss_array[:SEQ_SIZE])])[0]
	FLAT = kmeans.predict([numpy.array(flat_array[:SEQ_SIZE])])[0]

	idx = 0

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
			
			if res == GAIN and avg_short[-1] > avg_long[-1]:
				#compro
				if COINS == 0:
					num_coins = int((BUDGET - BUDGET * FEE) / data_ask[i] - 0.5)
					BUDGET = BUDGET - num_coins * (data_ask[i] + data_ask[i + 1]) / 2 - (data_ask[i] + data_ask[i + 1]) / 2 * FEE
					COINS = num_coins
			
			elif res == LOSS and avg_short[-1] < avg_long[-1]:				
				#vendo tutto
				if COINS > 0:
					BUDGET = BUDGET + COINS * (data_bid[i] + data_bid[i + 1]) / 2 - COINS * (data_bid[i] + data_bid[i + 1]) / 2 * FEE
					if BUDGET > INITIAL_BUDGET:
						diff = BUDGET - INITIAL_BUDGET
						PROFIT = PROFIT + BUDGET - INITIAL_BUDGET
						BUDGET = BUDGET - diff
					COINS = 0
			
			idx = idx + 1
	
	return (BUDGET + COINS * data_bid[-1] + PROFIT)