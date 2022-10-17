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
from scipy.stats import norm, mvn
from scipy.optimize import minimize, Bounds, OptimizeResult

from resourcecode.utils import set_trig


def censgaussfit(data: np.ndarray, q: float) -> OptimizeResult:
    """Fit a censored Gaussian (Nataf) Copula to the data

    Parameters
    ----------

    data: a NxM nd-array
    q: a float above which the model is fitted. Should be above 0.5.

    Returns
    -------

    res: OptimizeResult

        The optimization result represented as a OptimizeResult object.
        Important attributes are: x the solution array, success a Boolean
        flag indicating if the optimizer exited successfully and message
        which describes the cause of the termination. See `OptimizeResult
        <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.OptimizeResult.html#scipy.optimize.OptimizeResult>`_
        for a description of other attributes.
    """

    quantiles = np.quantile(data, q, axis=0)
    mask = np.ones(data.shape[0], dtype=bool)
    for i in range(data.shape[1]):
        mask = mask & (data[:, i] > quantiles[i])

    tail_dependency_obs = sum(mask) / data.shape[0]
    th_norm = norm.ppf(q)

    def fitness(cov):
        # For the 2D case, we have only one parameter
        if len(cov) > 1:
            sigma = np.eye(len(cov))
            set_trig(sigma, cov, "upper")
            set_trig(sigma, cov, "lower")
        else:
            sigma = cov

        return (
            tail_dependency_obs
            - mvn.mvnun(
                means=np.zeros_like(cov),
                covar=sigma,
                lower=np.full(len(cov), th_norm),
                upper=np.full(len(cov), np.inf),
            )[0]
        ) ** 2

    # to get the same result as R, I needed to transpose
    cov0 = np.corrcoef(data.T)[np.triu_indices(data.shape[1], k=1)]

    return minimize(
        fitness,
        cov0,
        bounds=Bounds(np.zeros_like(cov0), np.ones_like(cov0)),
        method="L-BFGS-B",
    )
