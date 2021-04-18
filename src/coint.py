import scipy.odr as odr
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller

class Coint:
    def __init__(self,feed,stock,etfs,period):
        #should be called in sth like next() in strat
        #period in trading days
        feed_dict = dict()
        for i,d in enumerate(feed.datas):
            feed_dict[d._name] = i
        self.stock_ret = self.log_ret(stock,feed,period)
        ret_list = []
        for etf in etfs:
            ret = self.log_ret(etf,feed,period)
            ret_list.append(ret)
        self.etf_ret = pd.DataFrame(ret_list).T
        pass
    
    def log_ret(self,tick,feed,period):
        data = pd.Series(feed.datas[self.feed_dict[tick]].close)[-period:]
        ret = np.log(data/data[0])
        return pd.Series(ret,index=data.index,name=tick)
    
    def regression(self):
        x = self.stock_ret.to_numpy()
        y = self.etf_ret.T.to_numpy()
        linmod = odr.Model(odr.multilinear.fcn)
        data = odr.Data(x, y)
        odrfit = odr.ODR(data, linmod, beta0=[1., 1., 1.])
        odrres = odrfit.run()
        self.betas = odrres.beta
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
