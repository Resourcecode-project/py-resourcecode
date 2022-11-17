# coding: utf-8

# Copyright 2020-2022 IFREMER (Brest, FRANCE), all rights reserved.
# contact -- mailto:nicolas.raillard@ifremer.fr
#
# This file is part of Resourcecode.
# Based on a R code written by Nicolas Raillard (nicolas.raillard@ifremer.fr)
#
# Resourcecode is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3.0 of the License, or any later version.
#
# Resourcecode is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with Resourcecode. If not, see <https://www.gnu.org/licenses/>.

import numpy as np

# from numpy.random import multivariate_normal
from scipy.stats import norm, genpareto, multivariate_normal

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

    rho: np.ndarray
        estimated correlation coefficient from censored Nataf Copulas.
        output of the CensGaussFit function.
    quant: float
        the quantile used for conditioning
    gpd_parameters: np.ndarray
        estimated threshold and GPD parameters.
        output of the get_gpd_parameters.
    n_simulations: int
        the requested number of simulations


    Returns
    -------

    simulations: A [NxM] numpy matrix with the result of the N simulations

    """
    nvar = len(gpd_parameters)

    # For the 2D case, we have only one parameter
    if len(rho) > 1:
        sigma = np.eye(nvar)
        set_trig(sigma, rho, "upper")
        set_trig(sigma, rho, "lower")
    else:
        sigma = np.eye(2)
        sigma[1, 0] = rho
        sigma[0, 1] = rho

    result = None
    while result is None or len(result) < n_simulations:
        simul = multivariate_normal.rvs(
            mean=np.full(nvar, 0),
            cov=sigma,
            size=n_simulations,
        )

        mask = simul[:, 0] > norm.ppf(quantile)
        for i in range(1, nvar):
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
