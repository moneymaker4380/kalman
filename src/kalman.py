import numpy as np
import pandas as pd
from pykalman import KalmanFilter
import scipy.odr as odr


class Kalman:
    def __init__(self, error_df, p_lags, adf_threshold):
        self.error_df = error_df
        self.p_lags = p_lags
        self.error_sd = self.error_df.std().squeeze()
        self.adf_threshold = adf_threshold
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
        means, covs = self.kf.filter(self.error_df)
        self.state_mean = means[-1]
        self.state_cov = covs[-1]
        pass

    def update(self, error_new, timestamp):
        self.error_df.append(pd.DataFrame(error_new, index=timestamp))
        obs = [1,self.error_df.shift(1).iloc[-1].squeeze()]
        obs.extend([self.error_df.diff().shift(i).iloc[-1].squeeze() for i in range(1,self.p_lags+1)])
        obs = np.array(obs)[np.newaxis]
        new_m, new_cov = self.kf.filter_update(filtered_state_mean = self.state_mean, filtered_state_covariance = self.state_cov, observation = error_new, observation_matrix = obs)
        self.state_mean = new_m.data
        self.state_cov = new_cov
        pass

    def tStat(self):
        return self.state_mean[1] / np.sqrt(self.state_cov[1, 1])

    def sr(self):
        return self.error_df.iloc[-1].squeeze()/self.error_sd

    def asr(self):
        return abs(self.error_df.iloc[-1].squeeze()/self.error_sd)

    def powerStat(self):
        return self.asr()**(self.adf_threshold - self.tStat())

