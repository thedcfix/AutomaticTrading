from recordclass import recordclass
from sklearn.cluster import KMeans
import pickle
import numpy
import gzip
import telepot
import time
import requests
import json

User = recordclass("User", ['id', 'wallet'])
Coin = recordclass("Coin", ['name', 'amount', 'investment', 'fee', 'last_ask', 'last_bid'])
Quotation = recordclass("Quotation", ['ask', 'bid'])
Log = recordclass('Log', ['coin', 'value_ask', 'value_bid'])
References = recordclass('References', ['GAIN', 'LOSS', 'FLAT'])

# -------------
#  classes
# -------------

class SuperQueue:
	def __init__(self, dim):
		self.items = []
		self.dim = dim
	
	def put(self, el):
		if len(self.items) == self.dim:
			self.items = self.items[1 :]
		self.items.append(el)
		
	def get(self):
		return self.items
		
	def clear(self):
		del self.items[:]
		self.dim = 0
		
	def changeSize(self, dim):
		self.dim = dim
		
	def show(self):
		print(self.items)

# -------------
#  functions
# -------------

def getQuotation(coin):
	coin = coin.upper()
	URI = "https://api.kraken.com/0/public/Ticker?pair="
	URI = URI + coin + "EUR"

	response = requests.get(URI)
	response = json.loads(response.text)
	
	result = Quotation(float(response["result"]["X" + coin + "ZEUR"]["a"][0]), float(response["result"]["X" + coin + "ZEUR"]["b"][0]))
	return result
	
def genExtractor(seq):
	
	SEQ_SIZE = seq
	
	with open('log.dat', 'rb') as infile:
		ledger = pickle.load(infile)
		
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
	
def getReferences():

	with open('log.dat', 'rb') as infile:
		ledger = pickle.load(infile)

	#valori fittizi, servono solo per l'inizializzazione degli array
	GAIN = 20
	FLAT = 20
	LOSS = 20
	gain_array = []
	loss_array = []
	flat_array = []
			
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
	
	return References(GAIN, LOSS, FLAT)
	
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

# -------------
#     main
# -------------

configFile = gzip.open("config","rb")
config = pickle.load(configFile)
configFile.close()

bot = telepot.Bot("467920869:AAF9JHOTFqOyCzyHa8yQ-DYRT9sQvztyfSg")

SEQ_SIZE = 25
SHORT_AVG = 865
LONG_AVG = 590
DAILY_RECORDS = 24 * 3600 / 45
BUDGET = 100
INITIAL_BUDGET = BUDGET
COINS = 0
PROFIT = 0
FEE = 0.26 / 100

logLedger = []
queueShort = SuperQueue(SHORT_AVG)
queueLong = SuperQueue(LONG_AVG)
values = SuperQueue(SEQ_SIZE)
res = -1

i = 0
idx = 0
	
while 1:

	try:
		# recupero la nuova quotazione
		for coin in config.wallet:
			quotation = getQuotation(coin.name)
			coin.last_ask = quotation.ask
			data_ask = quotation.ask
			coin.last_bid = quotation.bid
			data_bid = quotation.bid
			
		# vedo se aggiornare il kmeans (uno al giorno) e calcolo i nuovi GAIN, LOSS e FLAT
		if (i % DAILY_RECORDS == 0):
			kmeans = genExtractor(SEQ_SIZE)
			ref = getReferences()
			GAIN = ref.GAIN
			LOSS = ref.LOSS
			FLAT = ref.FLAT
		
		# eseguo le azioni di acquisto/vendita
		values.put(data_ask)
		queueShort.put(data_ask)
		queueLong.put(data_ask)
		
		# floating average short period
		avg_short = getFloatingAvg(queueShort, SHORT_AVG)
		
		# floating average long period
		avg_long = getFloatingAvg(queueLong, LONG_AVG)

		if i > SEQ_SIZE - 1:
			array = numpy.array(values.get())
			array = array / getAvg(array)
			array = array**(1/2)
			res = kmeans.predict([array])[0]
			
			if res == GAIN and avg_short > avg_long:
				#compro
				if COINS == 0:
					num_coins = int((BUDGET - BUDGET * FEE) / data_ask - 0.5)
					BUDGET = BUDGET - num_coins * data_ask - data_ask * FEE
					COINS = num_coins
					bot.sendMessage(config.id, "Ho comprato " + str(COINS) + " Ripple a " + str(data_ask))
			
			elif res == LOSS and avg_short < avg_long:				
				#vendo tutto
				if COINS > 0:
					BUDGET = BUDGET + COINS * data_bid - COINS * data_bid * FEE
					if BUDGET > INITIAL_BUDGET:
						diff = BUDGET - INITIAL_BUDGET
						PROFIT = PROFIT + BUDGET - INITIAL_BUDGET
						BUDGET = BUDGET - diff
						
					bot.sendMessage(config.id, "Ho venduto " + str(COINS) + " Ripple a " + str(data_bid) + ".\nBUDGET = " + str(BUDGET) + "\nPROFIT = " + str(PROFIT))
					
					COINS = 0
			
			idx += 1
		
		# salvo i dati nel log
		for coin in config.wallet:
			logLedger.append(Log(coin.name, coin.last_ask, coin.last_bid))
		
		with open('log_live.dat', 'wb') as outfile:
			pickle.dump(logLedger, outfile)
			
		i += 1
		
		print(str(i) + "\t" + str(data_ask) + "\t\t Trend: " + str(res) + "\t BUDGET: " + str(float("{0:.2f}".format(BUDGET))) + "\t" + str("up" if avg_short > avg_long else "down") 
				+ "\t PROFIT: " + str(float("{0:.4f}".format(PROFIT))))
		print("\n")

	except:
		print("Oh no, è sucesso qualcosa di brutto =(")

	time.sleep(45)