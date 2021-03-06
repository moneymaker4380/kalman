import scipy.odr as odr
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from get_data import GetData

class Coint:
    def __init__(self,feed,feed_dict,stock,etfs,period,adf_threshold):
        #should be called in sth like next() in strat
        #period in trading days
        self.eliminate = False
        self.openPos = False
        self.openSize = dict()
        self.nan_presence = False
        self.reference_price = dict()
        self.adf_threshold = adf_threshold
        self.feed_dict = feed_dict
        self.stock = stock
        self.etfs = etfs
        self.stock_ret = self.log_ret(stock,feed,period).ffill()
        ret_list = []
        for etf in etfs:
            ret = self.log_ret(etf,feed,period).ffill()
            ret_list.append(ret)
        self.etf_ret = pd.DataFrame(ret_list).T
        self.residuals_size = 252
        self.residuals = np.array([])
        self.regression()
        self.update_residual(x=self.etf_ret.to_numpy(), y=self.stock_ret.to_numpy())
        if self.nan_presence:
            return
        # self.residuals = pd.DataFrame(self.residual(x=self.etf_ret.to_numpy(), y=self.stock_ret.to_numpy()), index=self.stock_ret.index)
        self.res_std = np.std(self.residuals,ddof=1)
        #print(self.stock,self.powerStat(),self.t_stat)
        pass

    def log_ret(self,tick,feed,period):
        # print(tick)
        data = pd.Series(feed.datas[self.feed_dict[tick]].close.array)
        data = data.iloc[-period:] #no timestamp combining list of Series
        self.reference_price[tick] = data.iloc[0]
        ret = np.log(data/data.iloc[0])
        # pd.Series(ret, index=data.index, name=tick)
        return ret

    def regression(self):
        y = self.stock_ret.to_numpy()
        x = self.etf_ret.T.to_numpy()
        data = odr.Data(x=x, y=y) #x vertical is one observation
        odrfit = odr.ODR(data,odr.models.multilinear)
        odroutput = odrfit.run()
        # odroutput.pprint()
        self.beta = odroutput.beta
        return

    def adf(self, errors):
        adf = adfuller(errors, autolag='BIC')
        self.t_stat = adf[0]
        # print(self.stock, self.t_stat)
        self.p_lags = adf[2]
        #critical values
        # print(adf[4])
        pass

    def update_residual(self, x, y): #x horizontal is one observation
        x = np.insert(x,0,1,axis=1)
        self.residuals = np.append(self.residuals, (y-x.dot(self.beta))/np.sqrt(self.beta[1:].dot(self.beta[1:])+1))
        if len(self.residuals) > self.residuals_size:
            self.residuals = self.residuals[-self.residuals_size:]
        self.validation_nan()
        if self.nan_presence:
            return
        self.adf(self.residuals)
        pass

    def sr(self):
        return self.residuals[-1]/self.residuals.std(ddof=1)

    def powerStat(self):
        return abs(self.sr())**(self.adf_threshold - self.t_stat)

    def signal(self):
        sig = dict()
        multiplyer = 1
        if not self.openPos and (self.powerStat() > 1.3):
            if self.sr() > 0:
                multiplyer = -1
            self.openPos = True
            sig[self.stock] = 1 * multiplyer
            for i in range(len(self.etfs)):
                sig[self.etfs[i]] = -self.beta[i + 1] * multiplyer
        elif (self.powerStat() < 1.1):
            if not (self.t_stat < self.adf_threshold):
                self.eliminate = True
            if self.openPos:
                self.openPos = False
                return self.openSize
        return sig


    def validation_nan(self):
        self.nan_presence = np.isnan(self.residuals).any()