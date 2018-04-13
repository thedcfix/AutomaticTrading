from recordclass import recordclass
import pickle
import sys

Log = recordclass('Log', ['coin', 'value_ask', 'value_bid'])

DAY_NUM = int(sys.argv[1])

# one record every 45 seconds 24/7
DAILY_RECORDS = 24 * 3600 / 45

with open('log_completo.dat', 'rb') as infile:
	ledger = pickle.load(infile)
	
day = []
	
for el in range(0 + int((DAY_NUM - 1) * DAILY_RECORDS), int(DAY_NUM * DAILY_RECORDS)):
	day.append(ledger[el])
	
file = open('log.dat','wb')
pickle.dump(day, file)
file.close()