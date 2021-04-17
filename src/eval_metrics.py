from scipy.stats import norm

class EvalMetrics:
    def __init__(self,rfrate,simplereturn,ar,day):
        self.rfrate = 0.017
        self.logreturn 
        self.ar 
        self.day = 260

    def sharpe(self):
        Sharpe = ((self.logreturn.mean() - self.rfrate) / logreturn.std())
        return Sharpe

    def sortino(self):
        downsidereturn = df0.loc[df0['returns'] < 0.0]
        Sortino = ((self.logreturn.mean() - self.rfrate) / downsidereturn.std())
        return Sortino

    def calmar(self):
        Calmar = self.ar/self.md()
        return Calmar

    def cvar(self):
        alpha = 0.01
        CVaR = alpha**(-1) * norm.pdf(norm.ppf(alpha))*self.logreturn.std() - self.logreturn.mean()
        return CVaR

    def md(self):
        RollMax = self.logreturn.cummax()
        DailyDrawdown = self.logreturn/RollMax - 1.0
        MD = DailyDrawdown.cummin()
        return MD
