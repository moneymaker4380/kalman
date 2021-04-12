import backtrader as bt

class Strategy(bt.Strategy):
    def __int__(self):
        pass
    
cerebro = bt.Cerebro()
data = bt.feeds.PandasData(dataname=df0,
                           fromdate = datetime.datetime(2006, 1, 2),
                           todate = datetime.datetime(2020, 12, 31)
                          )
cerebro.adddata(data) 
cerebro.addstrategy(TestStrategy)
cerebro.broker.set_cash(cash=10000000)
cerebro.run()
cerebro.plot() 
