import numpy as np
import pandas as pd
from pykalman import KalmanFilter
import scipy.odr as odr


class Kalman:
    def __init__(self, error_df, n_lags):
        self.error_df = error_df
        self.n_lags = n_lags
        pass

    def create(self):
        lags = list(map(lambda x: self.error_df - self.error_df.shift(x), range(1, self.n_lags + 1)))
        lags.insert(0, self.error_df.shift(1))
        lags.insert(0, np.ones_like(self.error_df))
        self.obs = pd.concat(lags, axis=1)
        kf = KalmanFilter(n_dim_obs=1, n_dim_state=factors.shape[1],
                          transition_matrices=np.eye(factors.shape[1]),
                          observation_matrices=obs_matrix,
                          em_vars='transition_covariance, observation_covariance,''initial_state_mean, initial_state_covariance')
        pass

    def update(self):
        pass