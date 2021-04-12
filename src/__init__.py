###
# testing
###
import numpy as np
import pandas as pd
from pykalman import KalmanFilter
import statsmodels.sandbox.tools.tools_pca as spca
import statsmodels.api as ols
from matplotlib import pyplot as plt

if __name__ == "__main__":
    ...

xreduced, factors, evals, evecs =spca.pca(data=return, keepdim=I)
factors = ols.add_constant(factors)
obs_matrix = np.array(factors)[:,np.newaxis]
kf = KalmanFilter(n_dim_obs=1, n_dim_state=factors.shape[1],
                  transition_matrices=np.eye(factors.shape[1]),
                  observation_matrices=obs_matrix,
                  em_vars='transition_covariance, observation_covariance,'
                          'initial_state_mean, initial_state_covariance')

