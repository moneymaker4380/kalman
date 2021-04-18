import scipy.odr as odr
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from get_data import GetData

class Coint:
    def __init__(self,feed,feed_dict,stock,etfs,period):
        #should be called in sth like next() in strat
        #period in trading days
        self.feed_dict = feed_dict
        self.stock_ret = self.log_ret(stock,feed,period).ffill()
        ret_list = []
        for etf in etfs:
            ret = self.log_ret(etf,feed,period).ffill()
            ret_list.append(ret)
        self.etf_ret = pd.DataFrame(ret_list).T
        self.regression()
        self.residuals = pd.DataFrame(self.residual(x=self.etf_ret.to_numpy(), y=self.stock_ret.to_numpy()), index=self.stock_ret.index)
        self.adf(self.residuals)
        pass

    def log_ret(self,tick,feed,period):
        data = pd.Series(feed.datas[self.feed_dict[tick]].close.array)[-period:] #no timestamp combining list of Series
        ret = np.log(data/data.iloc[0])
        # pd.Series(ret, index=data.index, name=tick)
        return ret

    def regression(self):
        y = self.stock_ret.to_numpy()
        x = self.etf_ret.T.to_numpy()
        data = odr.Data(x=x, y=y) #x vertical is one observation
        odrfit = odr.ODR(data,odr.models.multilinear)
        odroutput = odrfit.run()
        odroutput.pprint()
        self.beta = odroutput.beta
        return

    def adf(self, errors):
        # set maxlag = 0?
        adf = adfuller(errors, autolag='BIC')
        self.t_stat = adf[0]
        self.p_lags = adf[2]
        # print('p-value: ', adf[1])
        #critical values
        print(adf[4])
        pass

    def residual(self, x, y): #x horizontal is one observation, etf logR but not yet added 1
        x = np.insert(x,0,1,axis=1)
        residuals = (y-x.dot(self.beta))/np.sqrt(self.beta.dot(self.beta)+1)
        return residuals


