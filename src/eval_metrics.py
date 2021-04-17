from scipy.stats import norm

class EvalMetrics:
    def __init__(self,rfrate,simplereturn,ar,day):
        self.rfrate = 0.017
        self.logreturn 
        self.ar 
        self.day = 260

    def sharpe(self):
        Sharpe = ((self.simplereturn.mean() - self.rfrate) / self.simplereturn.std())
        return Sharpe

    def sortino(self):
        downsidereturn = df0.loc[df0['returns'] < 0.0]
        Sortino = ((self.simplereturn.mean() - self.rfrate) / downsidereturn.std())
        return Sortino

    def calmar(self):
        Calmar = self.ar/self.md()
        return Calmar

    def cvar(self):
        alpha = 0.01
        CVaR = alpha**(-1) * norm.pdf(norm.ppf(alpha))*self.simplereturn.std() - self.simplereturn.mean()
        return CVaR

    def md(self):
        RollMax = self.simplereturn.cummax()
        DailyDrawdown = self.simplereturn/RollMax - 1.0
        MD = DailyDrawdown.cummin()
        return MD
