import numpy as np
import pandas as pd
from pykalman import KalmanFilter
import scipy.odr as odr


class Kalman:
    def __init__(self, error_df, p_lags):
        self.error_df = error_df
        self.p_lags = p_lags
        pass

    def create(self, error_cov):
        lags = self.error_df.diff()
        self.obs = [pd.DataFrame(np.ones_like(self.error_df)), self.error_df.shift(1)]
        self.obs.extend(list(map(lambda x: lags.shift(x), range(1,self.p_lags+1))))
        # lags.insert(0, self.error_df.shift(1))
        # lags.insert(0, np.ones_like(self.error_df))
        self.obs = pd.concat(self.obs, axis=1)
        self.obs.fillna(0, inplace=True)
        self.kf = KalmanFilter(transition_matrices = np.eye(2 + self.p_lags - 1 ),
                               observation_matrices = self.obs.to_numpy()[:,np.newaxis],
                               observation_covariance = error_cov,
                               em_vars='transition_covariance, initial_state_mean, initial_state_covariance')
        self.kf.
        pass

    def update(self, eNew, timestamp):
        self.error_df.append(pd.DataFrame(eNew, index=timestamp))
        obs = [self.error_df.shift(1)[-1]]
        obs.extend([self.error_df.diff().shift(i)[-1] for i in range(1,self.p_lags)])
        obs.append(list(map(lambda x: eNew)))
        pass