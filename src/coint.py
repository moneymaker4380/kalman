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
        self.residuals = np.array([])
        self.regression()
        self.update_residual(x=self.etf_ret.to_numpy(), y=self.stock_ret.to_numpy())
        # self.residuals = pd.DataFrame(self.residual(x=self.etf_ret.to_numpy(), y=self.stock_ret.to_numpy()), index=self.stock_ret.index)
        self.adf(self.residuals)
        self.res_std = np.std(self.residuals,ddof=1)
        pass

    def log_ret(self,tick,feed,period):
        data = pd.Series(feed.datas[self.feed_dict[tick]].close.array)[-period:] #no timestamp combining list of Series
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
        # print('p-value: ', adf[1])
        #critical values
        # print(adf[4])
        pass

    def update_residual(self, x, y): #x horizontal is one observation
        x = np.insert(x,0,1,axis=1)
        self.residuals = np.append(self.residuals, (y-x.dot(self.beta))/np.sqrt(self.beta.dot(self.beta)+1))
        self.adf(self.residuals)
        pass

    def sr(self):
        return self.residuals[-1]/self.res_std

    def asr(self):
        return abs(self.residuals[-1]/self.res_std)

    def powerStat(self):
        return self.asr()**(self.adf_threshold - self.t_stat)

    def signal(self):
        sig = dict()
        multiplyer = 1
        if self.t_stat < -2.0:
            # if self.openPos:
            #     multiplyer = 0
            #     self.openPos = False
            # else:
            #     multiplyer = 5
            # self.eliminate = True
            x = 1
        else:
            if not self.openPos and self.asr() > 2:
                if self.sr() > 0:
                    multiplyer = -1
                self.openPos = True
            elif self.openPos and self.asr() < 0.75:
                multiplyer = 0
                self.openPos = False
            else:
                multiplyer = 5
        if multiplyer == 5:
            return dict()
        sig[self.stock] = 1 * multiplyer
        for i in range(len(self.etfs)):
            sig[self.etfs[i]] = -self.beta[i+1] * multiplyer
        return sig
