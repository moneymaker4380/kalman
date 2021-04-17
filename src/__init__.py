###
# testing
###
import numpy as np
import pandas as pd
from pykalman import KalmanFilter
import statsmodels.sandbox.tools.tools_pca as spca
import statsmodels.api as ols
from datetime import datetime
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
    # for ticker in data.etf_list():
    #     stock = data.cerebro_stock(ticker)
    #     print(ticker)
    #     cerebro1.adddata(stock)

    pep = data.cerebro_stock('PEP')
    cerebro1.adddata(pep, name='PEP')

    # ko = data.cerebro_stock('KO')
    # cerebro1.adddata(ko, name='KO')

    #data0 = bt.feeds.YahooFinanceData(dataname='MSFT', fromdate=datetime(2011, 1, 1), todate=datetime(2012, 12, 31))
    #cerebro1.adddata(data0, name='KO')


    cerebro1.addstrategy(Strategy)

    cerebro1.addanalyzer(bt.analyzers.Calmar, _name='Calmar')
    cerebro1.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
    cerebro1.addanalyzer(bt.analyzers.DrawDown, _name='DD')
    cerebro1.addanalyzer(bt.analyzers.Returns, _name='Return')
    cerebro1.addanalyzer(bt.analyzers.TimeReturn, _name='CumulativeReturn')

    print('Starting Portfolio Value: %.2f' % cerebro1.broker.getvalue())
    run_time = cerebro1.run()
    run = run_time[0]

    print('Annualized Return:', run.analyzers.Return.get_analysis()['rnorm'])
    print('Cumulative Return:', run.analyzers.CumulativeReturn.get_analysis()[datetime(2020,12,31)])
    print('Sharpe Ratio:', run.analyzers.SharpeRatio.get_analysis()['sharperatio'])
    print('Maximum Drawdown:', run.analyzers.DD.get_analysis()['max']['drawdown'])
    print('Calmar Ratio:', run.analyzers.Calmar.calmar)

    print('Final Portfolio Value: %.2f' % cerebro1.broker.getvalue())

    cerebro1.plot(iplot=False)


# #Kalman Filter
# xreduced, factors, evals, evecs =spca.pca(data=return, keepdim=I)
#
# factors = ols.add_constant(factors)
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
