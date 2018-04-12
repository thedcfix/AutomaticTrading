import gzip
import json
import matplotlib
matplotlib.use('agg',warn=False, force=True)
from matplotlib import pyplot as plt
import pickle
from recordclass import recordclass
import requests
import telepot
from telepot.loop import MessageLoop
import time

User = recordclass("User", ['id', 'wallet'])
Coin = recordclass("Coin", ['name', 'amount', 'investment', 'fee', 'last_ask', 'last_bid'])
Quotation = recordclass("Quotation", ['ask', 'bid'])
Log = recordclass('Log', ['coin', 'value_ask', 'value_bid'])
	
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
	
def show(coin):
	values = []
	coin = coin.upper()

	with open('log.dat', 'rb') as infile:
		ledger = pickle.load(infile)

	for log in ledger:
		if log.coin == coin:
			values.append(log[1])

	plt.figure("Cryptocurrency trend")
	plt.plot(values, 'k', label=coin, color="dodgerblue")
	plt.savefig(coin + "_chart.png")
	
	img = open(coin + "_chart.png", 'rb')
	bot.sendPhoto(config.id, img)
	img.close()

	plt.gcf().clear()
	
def update():
	for coin in config.wallet:
		delta = (coin.last_ask * coin.amount - coin.investment)
		perc = delta / coin.investment
		bot.sendMessage(config.id, "Il prezzo attuale dei tuoi " + coin.name + " è " + str(coin.last_ask) + "€ e il valore totale della tua criptovaluta è " + str(float("{0:.2f}".format(coin.last_ask * coin.amount))) + "€ ( " + str(float("{0:.2f}".format(delta))) + "€ / " + str(float("{0:.2f}".format(perc * 100))) + "% ).")

def getlog():
	with open('log.dat', 'rb') as infile:
		bot.sendDocument(config.id, infile)	
		
def handle(msg):
	msg = msg['text']
	command = msg.split(" ")
	action = command[0].lower()
	
	if action == "update":
		actions[action]()
	elif action == "show":
		actions[action](command[1])
	elif action == "getlog":
		actions[action]()
		
		
# -------------
#   actions
# -------------

actions = { "update" : update,
            "show" : show,
			"getlog" : getlog
}
		
# -------------
#     main
# -------------

configFile = gzip.open("config","rb")
config = pickle.load(configFile)
configFile.close()

bot = telepot.Bot("467920869:AAF9JHOTFqOyCzyHa8yQ-DYRT9sQvztyfSg")
MessageLoop(bot, handle).run_as_thread()

logLedger = []
	
while 1:

	try:
		for coin in config.wallet:
			quotation = getQuotation(coin.name)
			coin.last_ask = quotation.ask
			coin.last_bid = quotation.bid
			print("Prezzo " + coin.name + ": " + str(coin.last_ask))
		
		# salvo i dati nel log
		for coin in config.wallet:
			logLedger.append(Log(coin.name, coin.last_ask, coin.last_bid))
		
		with open('log.dat', 'wb') as outfile:
			pickle.dump(logLedger, outfile)
	
	except:
		print("Oh no, è sucesso qualcosa di brutto =(")
	
	time.sleep(45)