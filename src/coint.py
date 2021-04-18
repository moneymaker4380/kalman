import scipy.odr as odr
import numpy as np
import pandas as pd
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
        y = self.stock_ret.to_numpy()
        x = self.etf_ret.T.to_numpy()
        data = odr.Data(x, y) #x vertical is one observation
        odrfit = odr.ODR(data,odr.models.multilinear)
        odroutput = odrfit.run()
        self.beta = odroutput.beta
        pass

    def adf(self):
        # eg spread = train.asset2 - model.params[0] * train.asset1
        adf = adfuller(self.errorDF, autolag='BIC')
        #set maxlag = 0?
        print('ADF Statistic: ', adf[0])
        print('p-value: ', adf[1])
        #critical values
        print(adf[4])
        pass

    def residual(self, y, x): #x horizontal is one observation, etf logR but not yet added 1
        x = np.insert(x,0,1,axis=1)
        residuals = (y-x.dot(self.beta))/np.sqrt(self.beta.dot(self.beta))
        return residuals

    