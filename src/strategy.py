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
        self.adf_threshold = -1.6
        self.pairs_num = 20
        self.vacancy = self.pairs_num
        self.init_days = 2520
        self.last_rebel = 0
        self.rebal_period = 30
        self.min_asr = 1
        self.pair_kalman = {}
        self.pair_betas = {}
        self.dataclose = self.datas[0].close
        self.stat = open('position.csv', mode='w')
        self.stat.write(','.join(['']+[d._name for d in self.datas]+['\n']))
        self.initBool = False
        self.stopFindPair = False
        self.inds = dict()
        self.feed_dict = dict()
        self.coint_dict = dict()
        self.current_pairs = [] #Assume pairs named by the stock in the pair
        for i, d in enumerate(self.datas):
            self.inds[d] = dict()
            self.inds[d]['log_return'] = LogReturn(d)
        pass

    def nextstart(self):
        # initialize pairs
        pass

    def next(self):
        print(len(self))
        if ((not self.initBool) and (len(self) == self.init_days)):
            for i, d in enumerate(self.datas):
                self.feed_dict[d._name] = i
            self.tarpos = pd.Series(np.zeros(len(self.feed_dict)),index = self.feed_dict.keys())
            self.pair_ratio = pd.Series(np.zeros(len(self.feed_dict)),index = self.feed_dict.keys())
            stocks_list = [d._name for d in self.datas][4:]
            self.pending_list, self.active_list = self.initialize(stocks_list)
            power_stat = dict()
            for ticker in self.active_list:
                coint = Coint(self, self.feed_dict, ticker, ['QUAL', 'USMV', 'VLUE', 'MTUM'], 300, adf_threshold=self.adf_threshold)
                if abs(coint.sr()) > self.min_asr and coint.t_stat <= self.adf_threshold:
                    power_stat[ticker] = coint.powerStat()
                    # power_stat.append(coint.powerStat())
                # else:
                    # power_stat.append(-1)
            power_stat = dict(sorted(power_stat.items(), key=lambda item: item[1], reverse=True))
            accepted = list(power_stat.keys())
            # power_stat = np.array(power_stat)
            # accepted = np.argwhere(power_stat > -1)
            # accepted_order = np.array([accepted[np.argsort(power_stat[accepted])[::-1]].squeeze()])

            if len(accepted) > self.pairs_num:
                tempticker = accepted[:self.pairs_num]
            else:
                tempticker = accepted
            #     tempticker = np.array(self.active_list)[accepted_order[:min(self.pairs_num,len(self.active_list))]]
            # else:
            #     tempticker = np.array(self.active_list)[accepted_order]

            if len(tempticker) > 0:
                for ticker in tempticker:
                    self.coint_dict[ticker] = Coint(self, self.feed_dict, ticker, ['QUAL', 'USMV', 'VLUE', 'MTUM'], 300, adf_threshold = self.adf_threshold)
                if len(self.coint_dict.keys()) <= self.pairs_num/2:
                    self.stopFindPair = True
            """
            print(coint.beta)
            print(coint.t_stat, coint.p_lags)
            kf = Kalman(coint.residuals,-2.0,coint.adf_betas,coint.adf_betas_cov,coint.adf_res_var)
            print(kf.state_mean)
            print(np.diag(kf.state_cov))
            print(kf.tStat())
            """
            self.initBool = True
            self.last_rebel = len(self)
        elif (self.initBool and (len(self) >= self.init_days)):
            if ((not self.stopFindPair and (len(self.coint_dict.keys()) <= self.pairs_num/2)) or (len(self) - self.last_rebel >= self.rebal_period)):
                #rebalance
                print(f'################### Rebalnceing on {self.datetime.datetime(ago=0)} ###################')
                stocks_list = [d._name for d in self.datas][4:]
                for i, d in enumerate(self.datas):
                    self.feed_dict[d._name] = i
                self.pending_list, self.active_list = self.initialize(stocks_list)
                if len(self.active_list) > 0:
                    power_stat = dict()
                    curr_pair = list(self.coint_dict.keys())
                    for ticker in self.active_list:
                        if ticker in curr_pair:
                            # power_stat.append(-1)
                            continue
                        coint = Coint(self, self.feed_dict, ticker, ['QUAL', 'USMV', 'VLUE', 'MTUM'], 300, adf_threshold = self.adf_threshold)
                        if (abs(coint.sr()) > self.min_asr) and (coint.t_stat <= self.adf_threshold):
                            power_stat[ticker] = coint.powerStat()
                        # else:
                        #     power_stat.append(-1)
                    power_stat = dict(sorted(power_stat.items(), key=lambda item: item[1], reverse=True))
                    accepted = list(power_stat.keys())

                    if len(accepted) > self.pairs_num:
                        tempticker = accepted[:self.pairs_num]
                    else:
                        tempticker = accepted

                    if len(tempticker) > 0:
                        for ticker in tempticker:
                            if len(self.coint_dict) >= self.pairs_num:
                                break
                            self.coint_dict[ticker] = Coint(self, self.feed_dict, ticker, ['QUAL', 'USMV', 'VLUE', 'MTUM'], 300, adf_threshold = self.adf_threshold)
                        if len(self.coint_dict) <= self.pairs_num / 2:
                            self.stopFindPair = True
                        else:
                            self.stopFindPair = False
                    self.last_rebel = len(self)
            signals = []
            # signals = [{'MSFT': 1, 'VTV': -0.5, 'VUG': -0.5}]  # Presented in ratios (stock comes first)

            for ticker in list(self.coint_dict.keys()):
                y = np.log(self.datas[self.feed_dict[ticker]].close[0]/self.coint_dict[ticker].reference_price[ticker])
                x = [np.log(self.datas[self.feed_dict[etf]].close[0]/self.coint_dict[ticker].reference_price[etf]) for etf in self.coint_dict[ticker].etfs]
                self.coint_dict[ticker].update_residual(np.array([x]), y)
                signal = self.coint_dict[ticker].signal()
                if len(signal) > 0:
                    signals.append(signal)
            if len(signals)!=0:
                #reset tar pos
                self.tarpos = pd.Series(np.zeros(len(self.feed_dict)),index = self.feed_dict.keys())
                self.close_pairs = []
                new_pairs = []
                for signal in signals:
                    ##cannot pass as list
                    #print(signal)
                    if pd.Series(list(signal.keys()))[0] not in self.current_pairs:
                        self.current_pairs.append(list(signal.keys())[0])
                        self.pair_ratio.loc[list(signal.keys())[0]] = [signal]
                        new_pairs.append(signal)
                    else:
                        self.current_pairs.remove(list(signal.keys())[0])
                        self.pair_ratio.loc[list(signal.keys())[0]] = np.nan
                        self.close_pairs.append(list(signal.keys())[0])

                        # print(self.datas[self.feed_dict[tick]])
                #Close position of stocks
                #self.tarpos = self.tarpos.astype('int')
                if len(self.close_pairs)>0:
                    for tick in self.close_pairs:
                        order = self.order_target_value(self.datas[self.feed_dict[tick]],target=0)
                        print(order)
                    self.vacancy = self.vacancy + len(self.close_pairs)
                        #order = self.broker.submit(order)

                curr_cash = self.broker.getcash()
                nominal = curr_cash/self.vacancy

                if len(signals) - len(self.close_pairs) > 0:
                    self.vacancy = self.vacancy - (len(signals) - len(self.close_pairs))

                for pair in new_pairs:
                    total_beta = sum(np.abs(list(pair.values())))
                    unit = nominal/total_beta
                    for tick, beta in pair.items():
                        self.tarpos.loc[tick] = unit*beta

                if len(self.current_pairs)>0:
                    for tick in self.current_pairs:
                        order = self.order_target_value(self.datas[self.feed_dict[tick]],target=self.tarpos.loc[tick])
                        print(order)
                        #order = self.broker.submit(order)
                for tick in ['QUAL','USMV','VLUE','MTUM']:
                    order = self.order_target_value(self.datas[self.feed_dict[tick]],target=self.tarpos.loc[tick])
                    print(order)
                    #if order is not None:
                        #order = self.broker.submit(order)

            for ticker in list(self.coint_dict.keys()):
                if self.coint_dict[ticker].eliminate:
                    self.coint_dict.pop(ticker)
            self.stat.write(str(self.datetime.datetime(ago=0)) + ',')
            for i, d in enumerate(self.datas):
                self.stat.write(str(self.broker.getposition(d).size) + ',')
            self.stat.write('\n')
            #print(self.positionsbyname['MSFT'])
    
    def initialize(self,stocks):
        pending = []
        active = []
        for ticker in stocks:
            if len(self.datas[self.feed_dict[ticker]].close) <300:
                pending.append(ticker)
            else:
                active.append(ticker)

        return pending, active
    
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
