import numpy as np
import pandas as pd
import backtrader as bt
import scipy.odr as odr
from datetime import datetime
import csv
from log_return import LogReturn
from coint import Coint
from kalman import Kalman
from get_data import GetData

class Strategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    # def notify_order(self, order):
    #     if order.status in [order.Submitted, order.Accepted]:
    #         # Buy/Sell order submitted/accepted to/by broker - Nothing to do
    #         return
    #
    #     # Check if an order has been completed
    #     # Attention: broker could reject order if not enough cash
    #     if order.status in [order.Completed]:
    #         if order.isbuy():
    #             self.log('BUY EXECUTED, %.2f' % order.executed.price)
    #         elif order.issell():
    #             self.log('SELL EXECUTED, %.2f' % order.executed.price)
    #
    #         self.bar_executed = len(self)
    #
    #     elif order.status in [order.Canceled, order.Margin, order.Rejected]:
    #         self.log('Order Canceled/Margin/Rejected')


    def __init__(self):
        self.pair_kalman = {}
        self.pair_betas = {}
        self.dataclose = self.datas[0].close
        self.stat = open('position.csv', mode='w')
        self.stat.write(','.join(['']+[d._name for d in self.datas]+['\n']))
        self.initBool = False
        self.inds = dict()
        self.feed_dict = dict()
        self.coint_dict = dict()
        self.powerStat = []
        self.current_pairs = [] #Assume pairs named by the stock in the pair
        for i, d in enumerate(self.datas):
            self.inds[d] = dict()
            self.inds[d]['log_return'] = LogReturn(d)
        pass

    def nextstart(self):
        # initialize pairs
        pass

    def next(self):
        if ((not self.initBool) and (len(self) == 2820)):
            stocks_list = [d._name for d in self.datas][4:]
            for i, d in enumerate(self.datas):
                self.feed_dict[d._name] = i
            self.tarpos = pd.Series(np.zeros(len(self.feed_dict)),index = self.feed_dict.keys())
            self.pair_ratio = pd.Series(np.zeros(len(self.feed_dict)),index = self.feed_dict.keys())
            for ticker in stocks_list:
                coint = Coint(self,self.feed_dict,ticker,['QUAL','USMV','VLUE','MTUM'],300,adr_threshold=-2.0)
                if coint.asr() > 1 and coint.t_stat <= -2.0:
                    self.powerStat.append(coint.powerStat())
                else:
                    self.powerStat.append(0)
            for ticker in np.array(stocks_list)[np.argsort(self.powerStat)[-15:]]:
                self.coint_dict[ticker] = Coint(self,self.feed_dict,ticker,['QUAL','USMV','VLUE','MTUM'],300,adr_threshold=-2.0)
            """
            print(coint.beta)
            print(coint.t_stat, coint.p_lags)
            kf = Kalman(coint.residuals,-2.0,coint.adf_betas,coint.adf_betas_cov,coint.adf_res_var)
            print(kf.state_mean)
            print(np.diag(kf.state_cov))
            print(kf.tStat())
            """
            self.initBool = True
        elif((self.initBool) and (len(self) >= 2820)):
            # signals = [{'MSFT': 1, 'VTV': -0.5, 'VUG': -0.5}]  # Presented in ratios (stock comes first)
            signals = []
            for ticker in list(self.coint_dict.keys()):
                y = np.log(self.datas[self.feed_dict[ticker]].close[0]/self.coint_dict[ticker].reference_price[ticker])
                x = [np.log(self.datas[self.feed_dict[etf]].close[0]/self.coint_dict[ticker].reference_price[etf]) for etf in self.coint_dict[ticker].etfs]
                self.coint_dict[ticker].update_residual(np.array([x]), y)
                signal = self.coint_dict[ticker].signal()
                if len(signal) == 0:
                    signals.append(signal)
            if len(signals)!=0:
                #reset tar pos
                self.tarpos = pd.Series(np.zeros(len(self.feed_dict)),index = self.feed_dict.keys())
                self.close_pairs = []
                for signal in signals:
                    ##cannot pass as list
                    if str(next(iter(signal))) not in self.current_pairs:
                        self.current_pairs.append(list(signal.keys())[0])
                        self.pair_ratio.loc[list(signal.keys())[0]] = [signal]
                    else:
                        self.current_pairs.remove(list(signal.keys())[0])
                        self.pair_ratio.loc[list(signal.keys())[0]] = np.nan
                        self.close_pairs.append(list(signal.keys())[0])
                for pair in self.current_pairs:
                    for tick in self.pair_ratio.loc[pair][0]:
                        self.tarpos.loc[tick] += self.pair_ratio.loc[pair][0][tick]/len(self.current_pairs)
                        print(self.datas[self.feed_dict[tick]])
                #Close position of stocks
                self.tarpos = self.tarpos.astype('int')
                if len(self.close_pairs)>0:
                    for tick in self.close_pairs:
                        order = self.order_target_percent(self.datas[self.feed_dict[tick]],target=0)
                        print(order)
                        #order = self.broker.submit(order)
                if len(self.current_pairs)>0:
                    for tick in self.current_pairs:
                        order = self.order_target_percent(self.datas[self.feed_dict[tick]],target=self.tarpos.loc[tick])
                        print(order)
                        #order = self.broker.submit(order)
                for tick in ['VTV','VUG']:
                    order = self.order_target_percent(self.datas[self.feed_dict[tick]],target=self.tarpos.loc[tick])
                    print(order)
                    #if order is not None:
                        #order = self.broker.submit(order)

            for ticker in list(self.coint_dict.keys()):
                if self.coint_dict[ticker].eliminate:
                    self.coint_dict.pop(ticker)
                """
                for i, d in enumerate(self.datas):
                    # self.log(f'{d._name} Close, {d.close[0]}')
                    #self.log(f'{d._name} Position: {self.broker.getposition(d)}')
                    # self.stat.write(str(self.broker.getposition(d).size)+',')
                    pos = self.getposition(d).size
                    if len(self) % (252) == (0):
                        self.buy(d,size=10000)
                    elif len(self) % (252) == 126:
                        self.sell(d,size=10000)
                """
            self.stat.write('\n')
            #print(self.positionsbyname['MSFT'])
    
    def close_pos(self,signal):
        pass
    
    def stop(self):





            #self.log('LogReturn, %.2f' % self.inds[0])


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
