import scipy.odr as odr
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from get_data import GetData

class Coint:
    def __init__(self,feed,stock,etfs):
        data = GetData()
        #should be called in sth like next() in strat
        feed_dict = dict()
        for i,d in enumerate(feed.datas):
            feed_dict[d._name] = i
        self.stock_ret = pd.Series(feed.datas[feed_dict[stock]].close).pct_change().dropna()
        ret_list = []
        for etf in etfs:
            ret = pd.Series(feed.datas[feed_dict[etf]].close).pct_change().dropna()
            ret_list.append(ret)
        self.etf_ret = pd.DataFrame(ret_list).T
        pass

    def regression(self):
        x = self.stock_ret.to_numpy()
        y = self.etf_ret.T.to_numpy()
        linmod = odr.Model(linfit)
        data = odr.Data(x, y)
        odrfit = odr.ODR(data, linmod, beta0=[1., 1., 1.])
        odrres = odrfit.run()
        odrres.pprint()
        pass

    def adf(self):
        # eg spread = train.asset2 - model.params[0] * train.asset1
        adf = adfuller(spread, maxlag=1)
        #set maxlag = 0?
        #or adf = adfuller(spread, autolag='BIC')
        print('ADF Statistic: ', adf[0])
        print('p-value: ', adf[1])
        #critical values
        print(adf[4])
        pass
