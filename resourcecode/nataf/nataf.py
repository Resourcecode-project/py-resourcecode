#!/usr/bin/env python3
# coding: utf-8

import numpy as np
from numpy.random import multivariate_normal
from scipy.stats import norm, genpareto

from resourcecode.utils import set_trig


def nataf_simulation(data, quantile, gpd_parameters, n_simulations=1000):
    sigma = np.eye(len(data))
    set_trig(sigma, data, "upper")
    set_trig(sigma, data, "lower")

    result = None
    while result is None or len(result) < n_simulations:
        simul = multivariate_normal(
            mean=np.full(len(data), 0),
            cov=sigma,
            size=n_simulations,
        )

        mask = simul[:, 0] > norm.ppf(quantile)
        for i in range(1, len(data)):
            mask = mask & (simul[:, i] > norm.ppf(quantile))

        simul = simul[mask]
        simul = genpareto.ppf(
            norm.cdf(simul - quantile),
            loc=gpd_parameters[:, 0],
            scale=gpd_parameters[:, 1],
            c=gpd_parameters[:, 2],
        )

        result = np.vstack((result, simul)) if result is not None else simul

    return result[:n_simulations, :]
