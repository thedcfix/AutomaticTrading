# AutomaticTrading

**GOAL** :

The goal of the project is to see if it&#39;s possible to create a trading bot capable of autonomously buying/selling every kind of stock in an automatic way. The idea is to use a mixed approach comprising classical technical analysis (moving averages) and a new intuition of mine, inspired by how SAGE (Serial Analysis of Gene Expression) works and involving machine learnig; the idea is to detect the right time to buy or sell a title.

**HOW IT WORKS** :

As said, the final result is the combination of two approaches:

1. **MACHINE LEARNIG** : given a series of values, the algorithm takes into accout every possible sequence of  length N.
(es: series = 1,2,3,4,5,6 and N = 4 ----> (1,2,3,4 ; 2,3,4,5 ; 3,4,5,6))
All of these sequences are then normalized by simply dividing them by their average value in order to have them comparable sequences centered around 1.
Done this, the generated sequences of length N are used as a input to generate a K-Means Clustering model having 3 clusters. One for the ascending sequences (GAIN), one for the descending ones (LOSS) and the last for the stable ones (FLAT). The precision in identifying trends in very high using this technique.

2. **TECHNICAL ANALYSIS** : once the trend has been identified using the machine learning model, the two moving averages are used to confirm the process. They give a BUY signal if the short average is above the long average and vice versa for the SELL signal. This because the short time moving average responds faster to changes than the long time one.

**THE PROBLEM:**

Detecting the best configuration means finding 3 parameters: N, the length of the short moving average and the length of the long moving average. Being a parameters discovery problem, time complexity becomes O(n^3).

To evaluate a configuration (set of 3 parameters), the code exploits the simulator; it essentially applies the parameters and runs a paper simulation against the historical log (log_completo.dat). In the end it evaluates the final value (BUDGET + PROFIT) of such configuration. The initial budget is set to 100. If the simulator reveals that the final BUDGET + PROFIT (profit is whatevere exceeds 100), I&#39;m gaining money with the configuration, otherwise I&#39;m loosing.

To overcome the unfeasibility of the problem, this code uses a couple of heuristics. These heuristics do not simulate every single configuration but randomly generate points. Points represent a configuration in which N is fixed and the other 2 variables are randomly generated in a finite number, (eg. 100 points for every N).
This kind of heuristics generates a function that gets plotted on a chart. By looking at the chart is then possible to see in which areas the funzion is getting maximixed.

![Alt text](Figure_1.png?raw=true)

(The image shows how, for day 44, low values of N lead to higher values in the simulation)

A second heuristic allows to better analyze those areas and come out with the best possible configuration.

 ![Alt text](Figure_2.png?raw=true)
 
(In this case it&#39;s possible to see that for day 44 the configurations having the higher values have short (moving average) ranging from 400 to 1800 while the values of long (moving average) are centered around 200 or 600. In this case use the single\_solver to analyze a configuration fixing N to a certain value and see how it evolves)

**THE CODE:**

All of the code makes use af a log containing the values sampled every X seconds and saved in the format (a list):

Log = recordclass(&#39;Log&#39;, [&#39;coin&#39;, &#39;value\_ask&#39;, &#39;value\_bid&#39;])

Having coin as a string (may be 'dollars', 'euros' etc.) and the othe two values as floating point numbers.

log\.dat contains the history of the title

- **Functions** : contains functions used by the scripts
- **Simulator** : accepts 3 parameters: N short long and shows you how the situation evolves in time by doing a paper simulation using your configuration
- **Chart** : shows you the trend of your data and the profit history based on the last configuration that has been simulated
- **Function 1**: shows you the relation between N and short (long in hidden). Is useful to visualize the best configurations and their value.
- **Function 2**: use it to expand the details about a configuration on the plane short-long and the corresponding value.
- **Super\_solver** : it&#39;s the heuristic that generates the points
- **Single\_solver** : use it to see how configurations evolve when N is fixed

The bot itself is not provided. Just use these algorithms to build yours. I personally use a Telegram Bot to control the interactions with the bot and send commands. Codify your actions directly in your script (make it resilient to crashes and unexpected inputs).
Once you find the best configuration (i.e. the one maximizing the profit) build a live simulator to test the model before using it. The data collection process should be no shorter than 3 months to start giving acceptable results.
