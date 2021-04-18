import numpy as np
import pandas as pd
import backtrader as bt
import math


class LogReturn(bt.Indicator):
    #plotlines = dict(logreturns=dict())

    lines = ('logreturns',)
    plotinfo = dict(plot=False)

    def next(self):
        # This makes sure enough bars have passed before trying to calcualte the log return.
        self.l.logreturns[0] = math.log(self.datas[0].open[0] / self.datas[0].open[-len(self.data) + 1])
