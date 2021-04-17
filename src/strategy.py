import numpy as np
import pandas as pd
import backtrader as bt
import scipy.odr as odr
from datetime import datetime
from log_return import LogReturn


class Strategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.pair_kalman = {}
        self.pair_betas = {}
        self.dataclose = self.datas[0].close
        self.logreturn = LogReturn(self.datas[0])
        pass

    def nextstart(self):
        # initialize pairs
        pass

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        # if not self.position:  #not in the market
        #     if next_long > 0:
        #         self.buy()  #enter long position
        #     elif next_short < 0:
        #         self.close()  #close long position
        pass

# def coint_test(self, stock_df, etf_df):
#     stockR = np.log(stock_df.div(stock_df[0]))
#     etfR = np.log(etf_df.div(etf_df[0]))
#
#     return betas, n_lags, t_stat,

#
# ###cointegration
# from statsmodels.tsa.stattools import coint
# def find_cointegrated_pairs(data):
#     n = data.shape[1]
#     pvalue_matrix = np.ones((n, n))
#     score_matrix = np.zeros((n, n))
#     keys = data.keys()
#     pairs = []
#     for i in range(n):
#         for j in range(i+1, n):
#             result = coint(data[keys[i]], data[keys[j]])
#             score_matrix[i,j] = result[0]
#             pvalue_matrix[i, j] = result[1]
#             if result[1] < 0.05:
#                 pairs.append((keys[i], keys[j]))
#     return score_matrix, pvalue_matrix, pairs #return p=lag
#             pvalue_matrix[i, j] = result[1]
#             if result[1] < 0.05:
#                 pairs.append((keys[i], keys[j]))
#     return pvalue_matrix, pairs #return p=lag, statistics
#
#
# #TLS
# def odr_line(z, x):
#     #Define a function to fit the data with.
#     """The line of best fit."""
#     m, c = z
#     y = m*x + c
#     return y
# linear = odr.Model(odr_line)
# mydata = RealData(x, y)
# myodr = odr.ODR(mydata, linear, beta0=[0]) #can be beta0=[0., 1.]
# output = myodr.run()
#
#
# ###ADF
# #set maxlag=0?
#
#
# def z_score(series):
#  return ((series - np.mean(series)) / np.std(series))
#
#
# ###cerebro
# cerebro = bt.Cerebro()
# data = bt.feeds.PandasData(dataname=df0,
#                            fromdate = datetime(2006, 1, 2),
#                            todate = datetime(2020, 12, 31)
#                           )
# cerebro.adddata(data)
# cerebro.addstrategy(TestStrategy)
# cerebro.broker.setcommission(commission=0.0)
# cerebro.broker.set_cash(cash=10000000)
# print('Starting Portfolio Value: %.2f' % cerebro1.broker.getvalue())
# import backtrader.analyzers as btanalyzers
# cerebro.addanalyzer(bt.analyzers.Calmar, _name = 'Calmar')
# cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name = 'SharpeRatio')
# cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DD')
# cerebro.run()
# print('Final Portfolio Value: %.2f' % cerebro1.broker.getvalue())
# print('CR:', strat.analyzers.Calmar.get_analysis())
# print('SR:', strat.analyzers.SharpeRatio.get_analysis())
# print('DD:', strat.analyzers.DW.get_analysis())
# cerebro.plot()
