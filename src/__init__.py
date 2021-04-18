###
# testing
###
import numpy as np
import pandas as pd
from pykalman import KalmanFilter
# import statsmodels.sandbox.tools.tools_pca as spca
# import statsmodels.api as ols
from datetime import datetime
from functools import reduce
import backtrader as bt
from matplotlib import pyplot as plt
from strategy import Strategy
from get_data import GetData

if __name__ == "__main__":
    # Create a cerebro entity
    cerebro1 = bt.Cerebro()
    cerebro1.broker.setcash(10000000.0)
    cerebro1.broker.set_coc(True)


    data = GetData()
    # for ticker in data.stock_list():
    #     stock = data.cerebro_stock(ticker)
    #     print(ticker)
    #     cerebro1.adddata(stock,name=ticker)
    # for ticker in data.etf_list():
    #     etf = data.cerebro_etf(ticker)
    #     print(ticker)
    #     cerebro1.adddata(etf,name=ticker)

    pep = data.cerebro_stock('PEP')
    pep.plotinfo.plot = False
    cerebro1.adddata(pep, name='PEP')

    ko = data.cerebro_stock('KO')
    ko.plotinfo.plot = False
    cerebro1.adddata(ko, name='KO')

    # data0 = bt.feeds.YahooFinanceData(dataname='SPY', fromdate=datetime(2006, 1, 1), todate=datetime(2020, 12, 31))
    # cerebro1.adddata(data0, name='SPY')
    # cerebro1.addobserver(bt.observers.Benchmark,
    #                          data=data0)

    cerebro1.addstrategy(Strategy)

    cerebro1.addanalyzer(bt.analyzers.Calmar, _name='Calmar')
    cerebro1.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
    cerebro1.addanalyzer(bt.analyzers.DrawDown, _name='DD')
    cerebro1.addanalyzer(bt.analyzers.AnnualReturn, _name='Return')
    cerebro1.addanalyzer(bt.analyzers.TimeReturn, _name='CumulativeReturn')
    cerebro1.addanalyzer(bt.analyzers.PeriodStats, _name='Stats')

    cerebro1.addobserver(bt.observers.Trades)
    cerebro1.addobserver(bt.observers.DrawDown)

    print('Starting Portfolio Value: %.2f' % cerebro1.broker.getvalue())
    run_time = cerebro1.run()
    run = run_time[0]

    print('Annualized Return:', (reduce(lambda x,y: x*y, [1 + k for i,k in run.analyzers.Return.get_analysis().items()])**(1/15)-1))
    print('Cumulative Return:', run.analyzers.CumulativeReturn.get_analysis()[datetime(2020,12,31)])
    print('Sharpe Ratio:', run.analyzers.SharpeRatio.get_analysis()['sharperatio'])
    print('Maximum Drawdown:', run.analyzers.DD.get_analysis()['max']['drawdown'])
    print('Calmar Ratio:', run.analyzers.Calmar.calmar)
    print('Annualized Volatility:', run.analyzers.Stats.get_analysis()['stddev'])

    #cerebro1.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    #pyfoliozer = run.analyzers.getbyname('pyfolio')
    #returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    # import pyfolio as pf
    # pf.create_full_tear_sheet(
    #     returns,
    #     positions=positions,
    #     transactions=transactions,
    #     gross_lev=gross_lev,
    #     live_start_date='2006-01-01',  # This date is sample specific
    #     round_trips=True)

    print('Final Portfolio Value: %.2f' % cerebro1.broker.getvalue())
# factors = ols.add_constant(factors)

    cerebro1.plot(iplot=False)


# #Kalman Filter
# xreduced, factors, evals, evecs =spca.pca(data=return, keepdim=I)
#
#
# obs_matrix = np.array(factors)[:,np.newaxis]
#
#
# from sklearn.decomposition import PCA
# pca = PCA(n_components = 6)
# pca.fit(return0)
# pca.explained_variance_ratio_.cumsum()
# print('The shape of the array after PCA is: ' , pca.components_.T.shape)
#
# cov_mat = np.cov(return1)
# eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)
# tot = sum(eigen_vals)
# var_exp = [(i / tot) for i in sorted(eigen_vals, reverse=True)]
# cum_var_exp = np.cumsum(var_exp)
# print(cum_var_exp）
