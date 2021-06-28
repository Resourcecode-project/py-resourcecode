#!/usr/bin/env python3
# coding: utf-8

import numpy as np
from numpy.random import multivariate_normal
from scipy.stats import norm, genpareto

from resourcecode.utils import set_trig


def run_simulation(
    rho: np.ndarray,
    quantile: float,
    gpd_parameters: np.ndarray,
    n_simulations: int = 1000,
) -> np.ndarray:
    """Run simulations from a fitted Nataf Model.

    Parameters
    ----------

    rho: estimated correlation coefficient from censored Nataf Copulas.
         output of the CensGaussFit function.
    quant: the quantile used for conditioning
    gpd_parameters: estimated threshold and GPD parameters.
        output of the get_gpd_parameters.
    n_simulations: the requested number of simulations


    Returns
    -------

    simulations: A [NxM] numpy matrix with the result of the N simulations

    """

    sigma = np.eye(len(rho))
    set_trig(sigma, rho, "upper")
    set_trig(sigma, rho, "lower")

    result = None
    while result is None or len(result) < n_simulations:
        simul = multivariate_normal(
            mean=np.full(len(rho), 0),
            cov=sigma,
            size=n_simulations,
        )

        mask = simul[:, 0] > norm.ppf(quantile)
        for i in range(1, len(rho)):
            mask = mask & (simul[:, i] > norm.ppf(quantile))

        simul = simul[mask]
        simul = genpareto.ppf(
            norm.cdf(simul - quantile),
            loc=gpd_parameters[:, 0],
            scale=gpd_parameters[:, 1],
            c=gpd_parameters[:, 2],
        )

        if result is None:
            result = simul
        else:
            result = np.vstack((result, simul))

    return result[:n_simulations, :]
