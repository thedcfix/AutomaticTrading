import numpy as np
import matplotlib.pyplot as plt
import csv
from collections import deque
from pylab import *
import pickle
from recordclass import recordclass
from functions import getFloatingAvg, genExtractor, SuperQueue

Log = recordclass('Log', ['coin', 'value_ask', 'value_bid'])

SHORT_AVG = 5
LONG_AVG = 20
# one record sampled every 45 seconds for 24 hours
DAILY_RECORDS = 24 * 3600 / 45

stock = []

with open('log.dat', 'rb') as infile:
	ledger = pickle.load(infile)

for log in ledger:
	stock.append(log.value_ask)

daily_avg = []
avg_short = []
avg_long = []
queue_short = SuperQueue(SHORT_AVG)
queue_long = SuperQueue(LONG_AVG)

counter = 0
days = 0
sum = 0
avg = 0

# calculating daily moving averages (short and long)
for value in stock:
	sum += value
	counter += 1
	avg = sum / counter
	
	if (counter == DAILY_RECORDS):
		sum /= DAILY_RECORDS
		daily_avg.append(sum)
		
		sum = 0
		counter = 0
		
		for av in daily_avg:
			queue_short.put(av)
			queue_long.put(av)
		
		avg_short.append(getFloatingAvg(queue_short, SHORT_AVG))
		avg_long.append(getFloatingAvg(queue_long, LONG_AVG))

# ------------------------------------------------------

with open('history', 'rb') as infile:
	history = pickle.load(infile)

# exposing the net profit
history[:] = [x - 100 for x in history]

plt.figure("Trend analysis")
plt.subplot(311)
plt.plot(stock, 'k', color="red", label="XRP")
legend(framealpha=0.5)
plt.subplot(312)
plt.plot(daily_avg, 'k', color="black", label="AVG_" + str("DAILY"))
plt.plot(avg_short, 'k', color="blue", label="AVG_" + str(SHORT_AVG))
plt.plot(avg_long, 'k--', color="blue", label="AVG_" + str(LONG_AVG))
legend(framealpha=0.5)
plt.subplot(313)
plt.plot(history, 'k', color="green", label="PROFIT_HISTORY")
plt.axhline(0, color='red')
legend(framealpha=0.5)
plt.show()