# coding: utf-8

# Copyright 2020-2022  IFREMER (Brest, FRANCE), all rights reserved.
# contact -- mailto:nicolas.raillard@ifremer.fr
#
# This file is part of Resourcecode.
# Based on a matlab code written by Christophe Maisondieu (christophe.maisondieu@ifremer.fr)
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

from typing import Optional
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy.special import gamma as gamma_function


@dataclass
class WeibullDistributionResult:
    """The resulting fitted parameters for a Weibull distribution

    Parameters
    ----------
    Ha: np.ndarray
        the values for which the distribution has been fitted
    x0: float
        the parameter of the Weibull distribution
    b: float
        the parameter of the Weibull distribution
    k: float
        the parameter of the Weibull distribution

    Attributes
    ----------
    P: np.ndarray
        P is the probability of exceedance  P(Hs > Ha)
    Ha: np.ndarray
        the values for which the distribution has been fitted
    x0: float
        the parameter of the Weibull distribution
    b: float
        the parameter of the Weibull distribution
    k: float
        the parameter of the Weibull distribution
    """

    Ha: np.ndarray
    x0: float
    b: float
    k: float
    P: np.ndarray = field(init=False)
    _MCFrHS: np.ndarray  # a private array, used for plot debugging eventually
    _X: np.ndarray
    _Y: np.ndarray
    _residual: float

    def __post_init__(self):
        self.P = np.exp(-(((self.Ha - self.x0) / self.b) ** self.k))


@dataclass
class WeatherWindowResult:
    """The resulting estimation

    Parameters
    ----------
    weibull_distribution_result: WeibullDistributionResult
        Weibull adjustment parameters

    tau: np.ndarray
        Persistence: Mean duration of periods for which Hs<Ha (Hours)

    PT: np.ndarray
        The probability of occurence of a weather window corresponding to
        sea-state having hs < hs_access_threshold

    number_events: np.ndarray
        number of events

    number_access_hours: np.ndarray
        number access hours

    number_waiting_hours: np.ndarray
        number waiting hours

    """

    weibull_distribution_result: WeibullDistributionResult
    tau: np.ndarray
    PT: np.ndarray
    number_events: np.ndarray
    number_access_hours: np.ndarray
    number_waiting_hours: np.ndarray


def compute_weather_windows(
    hs: pd.Series,
    month: int,
    hs_access_threshold: Optional[np.ndarray] = None,
):
    """Identification of weather windows

    Montly statistics
    NMI Method

    Based on EQUIMAR Deliverable D7.4.1 Procedures for Estimating Site
    Accessibility and Appraisal of Implications of Site Accessibility (T.
    Stallard,University of Manchester, UKJ-F. Dhedin, Sylvain Saviot and
    Carlos NogueraElectricité de France, France) August 2010

    and

    Walker RT, Johanning L, Parkinson R. (2011) Weather Windows for Device
    Deployment at UK test Site: Availability and Cost Implications, European
    Wave and Tidal Energy Conference, Southampton,  EWTEC2011.

    Parameters
    ----------
    hs: a pandas Series given the Significant Wave Height (m)
        with a datetime index.
    month: int, the month number for which the weather window should be
        computed.
    hs_access_threshold: an optional numpy array given the significant wave
                         height operational access threshold

    Returns
    -------
    results: a WeatherWindowResult
    """

    if hs_access_threshold is None:
        hs_access_threshold = np.linspace(1, 3, 5)

    assert hs.index.is_monotonic_increasing, "hs must be a pandas serie sorted by time"

    nb_years = len(set(hs.index.year))
    nb_hours_by_year = 744
    taui = np.arange(1, nb_hours_by_year + 1)

    hs_this_month = hs.loc[hs.index.month == month]
    duration = len(hs_this_month) / nb_years

    weibull_distribution_result = fit_weibull_distribution(hs_this_month)
    ha_bins = weibull_distribution_result.Ha
    x0 = weibull_distribution_result.x0
    b = weibull_distribution_result.b
    k = weibull_distribution_result.k
    P = weibull_distribution_result.P

    h_mean = b * gamma_function(1 + 1 / k) + x0
    gamma = k + 1.8 * x0 / (h_mean - x0)
    beta = 0.6 * gamma**0.287
    A = 35 / np.sqrt(gamma)

    tau = (A * (1 - P)) / (P * (-np.log(P)) ** beta)

    PT = np.empty((len(hs_access_threshold), nb_hours_by_year))
    number_events = np.empty((len(hs_access_threshold), nb_hours_by_year))

    for ind, hs_threshold in enumerate(hs_access_threshold):
        ibin = np.argmin(abs(ha_bins - hs_threshold))
        tt = tau[ibin]
        xi = taui / tt

        alpha = 0.267 * gamma * (hs_threshold / h_mean) ** (-0.4)
        C = gamma_function(1 + 1 / alpha) ** alpha
        Pxi = np.exp(-C * xi**alpha)

        ePa = (hs_threshold - x0) / b
        ePak = ePa**k
        Pa = np.exp(-ePak)
        PT[ind, :] = Pxi * (1 - Pa)

        # number of events with Hs<Hs and Duration < T - monthly
        number_events[ind, :] = duration * Pxi * (1 - Pa) / taui

    # mean duration of access time - monthly
    number_access_hours = duration * PT

    # mean duration of waiting time - monthly
    waiting_hours = (duration - number_access_hours) / number_events
    number_waiting_hours = np.where(waiting_hours > duration, duration, waiting_hours)

    return WeatherWindowResult(
        weibull_distribution_result=weibull_distribution_result,
        tau=tau,
        PT=PT,
        number_events=number_events,
        number_access_hours=number_access_hours,
        number_waiting_hours=number_waiting_hours,
    )


def fit_weibull_distribution(hs: pd.Series) -> WeibullDistributionResult:
    """Fit a Weibull distribution on Hs.

        The probability of excedence :math:`P(Hs > Ha)` follows a Weibull
        distribution given by three parameters:

        :math:`P(Hs > Ha) = exp(-((Ha - x0)/b)^k)`

    Parameters
    ----------
    hs: a pandas Series
        giving the Significant Wave Height (m) with a datetime index.

    Returns
    -------
    weibull_distribution_result: WeibullDistributionResult
    """

    # hs cumulative distribution
    dbin = 0.1
    edges = np.arange(hs.min(), hs.max() + dbin, dbin)
    bins = 0.5 * (edges[:-1] + edges[1:])

    FrHs = np.histogram(hs, edges)[0] / len(hs)
    MCFrHs = 1 - FrHs.cumsum()
    MCFrHs[MCFrHs <= 0] = 1e-9

    Y = np.log(np.log(1 / MCFrHs))

    previous_residual, residual = 0, 1
    x0 = 0.0
    dx = 5e-3
    while True:
        previous_residual = residual
        x = x0 - dx
        x0 = x0 + dx
        X = np.log(bins - x0)

        ([p0, p1], [residual], _, _, _) = np.polyfit(X, Y, 1, full=True)

        if residual <= previous_residual:
            # SC: in my opinion, we should update k and b, and then break if the
            # new residual is lower than the previous one.
            # however, to get the same result as the matlab code, I have to do
            # that…
            break

        k, b = p0, np.exp(-p1 / p0)

    return WeibullDistributionResult(
        Ha=bins,
        x0=x,
        b=b,
        k=k,
        _MCFrHS=MCFrHs,
        _X=X,
        _Y=Y,
        _residual=residual,
    )


if __name__ == "__main__":
    hs = pd.read_csv(
        "../codes_to_migrate/matlab_codes/hs.csv",
        index_col=0,
        parse_dates=True,
    ).hs  # we want a Serie

    hs = hs[hs.index.year < 1997]

    for month in range(1, 13):
        r = compute_weather_windows(hs, month=month)
