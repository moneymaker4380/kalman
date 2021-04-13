import numpy as np
import backtrader as bt
from datetime import datetime

class Strategy(bt.Strategy):
    def __int__(self):
        pass
    
    
###cointegration
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


#TLS
import scipy.odr as odr
def odr_line(p, x):
    """The line of best fit."""
    #unpack the parameters:
    y = p*x
    return y
linear = odr.Model(odr_line)
mydata = odr.Data(x, y, wd=1./xerror, we=1./yerror)
myodr = odr.ODR(mydata, linear, beta0=[0])
output = myodr.run()


###ADF
from statsmodels.tsa.stattools import adfuller
#eg spread = train.asset2 - model.params[0] * train.asset1
adf = adfuller(spread, maxlag = 1)
#or adf = adfuller(spread, autolag='BIC')
print('ADF Statistic: ', adf[0])
print('p-value: ', adf[1])
#critical values
print(adf[4])

def z_score(series):
 return ((series - np.mean(series)) / np.std(series))


###cerebro
cerebro = bt.Cerebro()
data = bt.feeds.PandasData(dataname=df0,
                           fromdate = datetime.datetime(2006, 1, 2),
                           todate = datetime.datetime(2020, 12, 31)
                          )
cerebro.adddata(data) 
cerebro.addstrategy(TestStrategy)
cerebro.broker.setcommission(commission=0.0)
cerebro.broker.set_cash(cash=10000000)
print('Starting Portfolio Value: %.2f' % cerebro1.broker.getvalue())
cerebro.addanalyzer(bt.analyzers.Calmar, _name = 'Calmar')
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name = 'SharpeRatio')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DD')
cerebro.run()
print('Final Portfolio Value: %.2f' % cerebro1.broker.getvalue())
print('CR:', strat.analyzers.Calmar.get_analysis())
print('SR:', strat.analyzers.SharpeRatio.get_analysis())
print('DD:', strat.analyzers.DW.get_analysis())
cerebro.plot()
