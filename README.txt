Scopo:
data una sequenza di valori relativi all'andamento del valore di una criptovaluta/azione/altro, usare uno strumento di analisi tecnica (medie mobili) da affiancare ad un approccio basato sul machine learnig al fine di individuare il momento migliore per vendere/comprare un titolo.

Come funziona:
l'approccio si basa sull'analisi di sequenze (di lunghezza N da determinare) di valori appartenenti alla serie temporale da gestire. Sulla base dei dati raccolti in un log, campionati ogni 45 secondi, vengono generate tutte le possibli sequenze in esso contenute (es. sequenza: 1,2,3,4,5,6 con lunghezza 4. Si generano: 1,2,3,4 ; 2,3,4,5 ; 3,4,5,6).
Queste sequenze vengono poi normalizzate sulla base della media al fine di avere sequenze comparabili i cui valori oscillano in un intorno di 1.
Fatto ciò, queste sequenze sono utilizzate come input in un modello di clustering con tecnica K-Means. Il numero di cluster è impostato a 3 per raggruppare sequenze crescenti, decrescenti e stazionarie.
Nell'esecuzione live, il modello è usato per associare in tempo reale un sequenza in divenire ad uno dei 3 cluster. Questo consente di identificare con un'elevata precisione il tipo di trend in atto.
Una volta identificato il trend si utilizzano le medie mobili per identificare il miglior momento di acquisto/vendita. Anche le lunghezze delle medie mobili, misurate in campionamenti, sono parametri da determinare.
Quando la media di breve periodo è > di quella di lungo, significa che il trend in atto è positivo (la media risponde prima alla variazione di valore). Questo feedback genera un segnale di acuisto. Il viceversa genera un segnale di vendita.

Il problema:
l'individuazione della configurazioen migliore ricade in un problema di parameters discovery ed essendo i parametri da scoprire 3, l'algoritmo ha complessità O(n^3). Per ovviare a questo sono utilizzate delle euristiche, che generano K punti per ogni configurazione con valori causali per ognuna delle vaiabili (es. per N = 3 si generano 50 punti, cieè si 