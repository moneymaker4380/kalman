import numpy as np
import pandas as pd
from pykalman import KalmanFilter
import scipy.odr as odr

class Kalman:
    def __init__(self, error_df, adf_threshold, prior_state_mean, prior_state_cov, obs_cov):
        self.error_df = error_df
        self.error_sd = self.error_df.std().squeeze()
        self.adf_threshold = adf_threshold
        self.create(prior_state_mean,prior_state_cov,obs_cov)
        pass

    def create(self,prior_state_mean,prior_state_cov,obs_cov):
        # lags = self.error_df.diff()
        self.obs = [pd.DataFrame(np.ones_like(self.error_df), index=self.error_df.index), self.error_df.shift(1).iloc]
        # self.obs.extend(list(map(lambda x: lags.shift(x), range(1,self.p_lags))))
        # lags.insert(0, self.error_df.shift(1))
        # lags.insert(0, np.ones_like(self.error_df))
        self.obs = pd.concat(self.obs, axis=1, ignore_index=True)
        # self.obs.fillna(0, inplace=True)
        # transit_mx =
        # transit_mx[[0,1],[0,1]] = 1
        # transit_off = np.ones(2)
        # transit_off[[0,1]] = 0
        self.kf = KalmanFilter(transition_matrices = np.eye(2),
                               observation_matrices = self.obs.to_numpy()[:,np.newaxis],
                               observation_covariance = np.array([[obs_cov]]),
                               initial_state_mean = prior_state_mean,
                               initial_state_covariance = prior_state_cov,
                               em_vars='transition_covariance')
        means, covs = self.kf.filter(self.error_df)
        self.state_mean = means[-1]
        self.state_cov = covs[-1]
        pass

    def update(self, error_new, timestamp):
        self.error_df.append(pd.DataFrame(error_new, index=timestamp))
        obs = [1,self.error_df.shift(1).iloc[-1].squeeze()]
        # obs.extend([self.error_df.diff().shift(i).iloc[-1].squeeze() for i in range(1,self.p_lags)])
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

