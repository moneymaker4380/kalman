import numpy as np
import pandas as pd
import os
import backtrader as bt
"""            
        self.stock_dict = {'last':[self.STOCK_PX_LAST, 'PX_LAST'],'volume':[self.STOCK_PX_VOLUME,'PX_VOLUME'],
                           'equity_weighted_average_price':[self.STOCK_EQY_WEIGHTED_AVG_PX, 'EQY_WEIGHTED_AVG_PX']}
        self.etf_dict = {'last':[self.ETF_PX_LAST, 'PX_LAST'],'volume':[self.ETF_PX_VOLUME,'PX_VOLUME'],
                         'high':[self.ETF_PX_HIGH, 'PX_HIGH'],'open':[self.ETF_PX_VOLUME,'PX_OPEN'],
                         'low':[self.ETF_PX_LOW, 'PX_LOW'],'vwap_volume':[self.ETF_VWAP_VOLUME,'VWAP_VOLUME'],
                         'fund_net_asset_value':[self.ETF_FUND_NET_ASSET_VAL, 'FUND_NET_ASSET_VAL'],
                         'equity_weighted_average_price':[self.ETF_EQY_WEIGHTED_AVG_PX, 'EQY_WEIGHTED_AVG_PX']}
"""
class GetData:
    def __init__(self):
        for file in os.listdir('./data'):
            exec(f'self.{file.split(".")[0]} = pd.read_pickle("./data/{file}","gzip")')
        self.stock_dict = {'last':self.STOCK_PX_LAST,'volume':self.STOCK_PX_VOLUME,
                           'equity_weighted_average_price':self.STOCK_EQY_WEIGHTED_AVG_PX}
        self.etf_dict = {'last':self.ETF_PX_LAST,'volume':self.ETF_PX_VOLUME,
                         'high':self.ETF_PX_HIGH,'open':self.ETF_PX_VOLUME,
                         'low':self.ETF_PX_LOW,'vwap_volume':self.ETF_VWAP_VOLUME,
                         'fund_net_asset_value':self.ETF_FUND_NET_ASSET_VAL,
                         'equity_weighted_average_price':self.ETF_EQY_WEIGHTED_AVG_PX}
        pass
    
    def get_stock(self,ticker,prop):
        df = self.stock_dict[prop]
        return df.loc[:,ticker]
    
    def get_stock_all(self,ticker):
        temp = pd.DataFrame()
        for prop in self.stock_dict:
            temp = temp.append(self.stock_dict[prop].loc[:,ticker].rename(prop))
        return temp.T
    
    def get_etf(self,ticker,prop):
        df = self.etf_dict[prop]
        return df.loc[:,ticker]
    
    def get_etf_all(self,ticker):
        temp = pd.DataFrame()
        for prop in self.etf_dict:
            temp = temp.append(self.etf_dict[prop].loc[:,ticker].rename(prop))
        return temp.T
    
    def cerebro_stock(self,ticker):
        df = self.get_stock_all(ticker).iloc[:,:2]
        return StockFeed(df)
    
    def cerebro_etf(self,ticker):
        df = self.get_etf_all(ticker).iloc[:,:5]
        return EtfFeed(df)
        
  
class StockFeed(bt.feeds.DataBase):
    params = (
        ('open', None),
        ('high', None),
        ('low', None),
        ('close', 0),
        ('volume', 1),
        ('openinterest', None)
    )  

class EtfFeed(bt.feeds.DataBase):
    params = (
        ('open', 3),
        ('high', 2),
        ('low', 4),
        ('close', 0),
        ('volume', 1),
        ('openinterest', None)
    ) 
