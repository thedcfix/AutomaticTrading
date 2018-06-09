import numpy as np
import matplotlib.pyplot as plt
import csv
from collections import deque
from pylab import *
import pickle
from recordclass import recordclass
from functions import getFloatingAvg
from functions import genExtractor, getProfitHistory

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

# siti da cui scaricare le quotazioni in telpo reale
#https://it.investing.com/equities/adv-micro-device
#http://www.investopedia.com/markets/stocks/amd/?ad=dirN&qo=investopediaSiteSearch&qsrc=0&o=40186

#dati storici
#https://finance.yahoo.com/quote/AMD/history?p=AMD

SHORT_AVG = 13
LONG_AVG = 5

Log = recordclass('Log', ['coin', 'value_ask', 'value_bid'])

with open('log.dat', 'rb') as infile:
	ledger = pickle.load(infile)

stock = []
volume = []
xes = []
mins = []
queueShort = deque([], SHORT_AVG)
queueLong = deque([], LONG_AVG)
avg5 = []
avg20 = []

for log in ledger:
	if log.coin == "XRP":
		stock.append(log.value_ask)

#plt.axis("off")

mins.append(stock[0]);
xes.append(0);

# idetifico i minimi e le loro coordinate sulle ascisse
for i in range(len(stock) - 2):		
	if stock[i+1] < stock[i] and stock[i+2] > stock[i+1]:
		mins.append(stock[i+1]);
		xes.append(i+1);
		
for i in range(len(stock)):
	queueShort.appendleft(stock[i])
	queueLong.appendleft(stock[i])
	
	# floating average 5 days	
	fibo = 0
	sum = 0
	size = SHORT_AVG
		
	for i in queueShort:
		fibo += size
		sum += size * i
		size -= 1
	
	avg5.append(sum / fibo)
	
	# floating average 20 days
	fibo = 0
	sum = 0
	size = LONG_AVG
		
	for i in queueLong:
		fibo += size
		sum += size * i
		size -= 1
	
	avg20.append(sum / fibo)
	
	
# ---------------

Log = recordclass('Log', ['coin', 'value_ask', 'value_bid'])

# un record ogni 45 secondi per 24 ore
DAILY_RECORDS = 24 * 3600 / 45

with open('log.dat', 'rb') as infile:
	ledger = pickle.load(infile)
	
daily_avg = []
counter = 0
days = 0
sum = 0
avg = 0
avg_five = []
avg_twenty = []
els = SuperQueue(5)
elss = SuperQueue(20)
	
for log in ledger:
	sum += log.value_ask
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

# ---------------

# SEQ = 34
# short = 865
# long = 590

# kmeans = genExtractor(SEQ, ledger)
# history = getProfitHistory(SEQ, short, long, kmeans, ledger)

plt.figure("Trend analysis")
plt.subplot(211)
plt.plot(stock, 'k', label="Stock")
plt.plot(xes, mins, 'k', color="red", label="Trend");
legend(framealpha=0.5)
plt.subplot(212)
plt.plot(daily_avg, 'k', color="black", label="AVG_" + str("DAILY"))
plt.plot(avg_five, 'k', color="blue", label="AVG_" + str("5"))
plt.plot(avg_twenty, 'k--', color="blue", label="AVG_" + str("20"))
legend(framealpha=0.5)
# plt.subplot(313)
# plt.plot(history, 'k', color="green", label="PROFIT_HISTORY")
# legend(framealpha=0.5)
plt.show()