import scipy.odr as odr
from statsmodels.tsa.stattools import adfuller



class TLS:
    def __init__(self, stock_df, etf_df):
        pass

    def regression(self, y, x):

        return betas

    def adf(self):
        # eg spread = train.asset2 - model.params[0] * train.asset1
        adf = adfuller(spread, maxlag=1)  # eg spread = train.asset2 - model.params[0] * train.asset1
        set
        # maxlag = 0?
        adf = adfuller(spread, maxlag=1)
        # or adf = adfuller(spread, autolag='BIC')
        print('ADF Statistic: ', adf[0])
        print('p-value: ', adf[1])
        # critical values
        print(adf[4])
        pass