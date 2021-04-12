###
# testing
###
import numpy as np
import pandas as pd
from pykalman import KalmanFilter
import statsmodels.sandbox.tools.tools_pca as spca
import statsmodels.api as ols
import backtrader as bt
from matplotlib import pyplot as plt

if __name__ == "__main__":
    # Create a cerebro entity
    cerebro1 = bt.Cerebro()
    cerebro1.broker.setcash(10000000.0)

    print('Starting Portfolio Value: %.2f' % cerebro1.broker.getvalue())

    print('Final Portfolio Value: %.2f' % cerebro1.broker.getvalue())

#Kalman Filter
xreduced, factors, evals, evecs =spca.pca(data=return, keepdim=I)

factors = ols.add_constant(factors)

obs_matrix = np.array(factors)[:,np.newaxis]

kf = KalmanFilter(n_dim_obs=1, n_dim_state=factors.shape[1],
                  transition_matrices=np.eye(factors.shape[1]),
                  observation_matrices=obs_matrix,
                  em_vars='transition_covariance, observation_covariance,'
                          'initial_state_mean, initial_state_covariance')

from sklearn.decomposition import PCA
pca = PCA(n_components = 6) 
pca.fit(return0) 
pca.explained_variance_ratio_.cumsum()
print('The shape of the array after PCA is: ' , pca.components_.T.shape)

cov_mat = np.cov(return1)
eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)
tot = sum(eigen_vals)
var_exp = [(i / tot) for i in sorted(eigen_vals, reverse=True)]
cum_var_exp = np.cumsum(var_exp)
print(cum_var_exp）
