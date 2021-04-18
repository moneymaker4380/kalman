import scipy.odr as odr
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller

class Coint:
    def __init__(self,feed,feed_dict,stock,etfs,period):
        #should be called in sth like next() in strat
        #period in trading days
        self.feed_dict = feed_dict
        self.stock_ret = self.log_ret(stock,feed,period)
        ret_list = []
        for etf in etfs:
            ret = self.log_ret(etf,feed,period)
            ret_list.append(ret)
        self.etf_ret = pd.DataFrame(ret_list).T
        self.regression()
        self.residual(x=self.etf_ret.to_numpy(), y=self.stock_ret.to_numpy)
        self.adf(self.residuals)
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
        return

    def adf(self, errors):
        # set maxlag = 0?
        adf = adfuller(errors, autolag='BIC')
        self.t_stat = adf[0]
        self.p_lags = adf[2]
        # print('p-value: ', adf[1])
        #critical values
        self.crit_val = adf[4]
        # self.power_stat = abs(np.std(errors,ddof=1))
        pass

    def residual(self, x, y): #x horizontal is one observation, etf logR but not yet added 1
        x = np.insert(x,0,1,axis=1)
        residuals = (y-x.dot(self.beta))/np.sqrt(self.beta.dot(self.beta))
        self.residuals = pd.DataFrame(residuals, index=self.stock_ret.index)


