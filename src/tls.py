import scipy.odr as odr
from statsmodels.tsa.stattools import adfuller
from get_data import GetData

class TLS:
    def __init__(self,stock,etfs):
        data = GetData()
        self.stock_ret = data.get_stock(stock,'last').pct_change().dropna()
        ret_list = []
        for etf in etfs:
            ret = data.get_etf(etf,'last').pct_change().dropna()
            ret_list.append(ret)
        self.etf_ret = pd.DataFrame(ret_list).T
        pass

    def regression(self):
        odr.multilinear.fcn
        pass

    def adf(self):
        # eg spread = train.asset2 - model.params[0] * train.asset1
        adf = adfuller(spread, maxlag=1)  # eg spread = train.asset2 - model.params[0] * train.asset1
        set
        maxlag = 0?
        adf = adfuller(spread, maxlag=1)
        # or adf = adfuller(spread, autolag='BIC')
        print('ADF Statistic: ', adf[0])
        print('p-value: ', adf[1])
        # critical values
        print(adf[4])
        pass