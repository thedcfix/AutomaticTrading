from recordclass import recordclass
import pickle
import sys

Log = recordclass('Log', ['coin', 'value_ask', 'value_bid'])

DAY_NUM = int(sys.argv[1])

# un record ogni 45 secondi per 24 ore
DAILY_RECORDS = 24 * 3600 / 45

with open('log_completo.dat', 'rb') as infile:
	ledger = pickle.load(infile)
	
day = []
	
for el in range(0 + int((DAY_NUM - 1) * DAILY_RECORDS), int(DAY_NUM * DAILY_RECORDS)):
	day.append(ledger[el])
	
#file = open('log_day_' + str(DAY_NUM) + '.dat','wb')
file = open('log.dat','wb')
pickle.dump(day, file)
file.close()