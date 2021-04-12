import backtrader as bt
from datetime import datetime
import numpy as np

class Strategy(bt.Strategy):
    def __int__(self):
        pass
    
#cointegration
from statsmodels.tsa.stattools import coint
def find_cointegrated_pairs(data):
    n = data.shape[1]
    pvalue_matrix = np.ones((n, n))
    keys = data.keys()
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            result = coint(data[keys[i]], data[keys[j]])
            pvalue_matrix[i, j] = result[1]
            if result[1] < 0.05:
                pairs.append((keys[i], keys[j]))
    return pvalue_matrix, pairs

#ADF
from statsmodels.tsa.stattools import adfuller
spread = train.asset2 - model.params[0] * train.asset1
adf = adfuller(spread, maxlag = 1)
print('Critical Value = ', adf[0])
# probablity critical values
print(adf[4])

def z_score(series):
 return ((series - np.mean(series)) / np.std(series))

#cerebro
cerebro = bt.Cerebro()
data = bt.feeds.PandasData(dataname=df0,
                           fromdate = datetime.datetime(2006, 1, 2),
                           todate = datetime.datetime(2020, 12, 31)
                          )
cerebro.adddata(data) 
cerebro.addstrategy(TestStrategy)
cerebro.broker.set_cash(cash=10000000)
cerebro.run()
cerebro.plot() 
