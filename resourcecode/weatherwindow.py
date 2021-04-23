#!/usr/bin/env python3
# coding: utf-8

from typing import Optional

import numpy as np
import pandas as pd
from scipy.special import gamma as gamma_function


def compute_weather_windows(
    hs: pd.Series,
    month,
    hs_access_threshold: Optional[np.array] = None,
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
    hs_access_threshold: an optional numpy array given the significant wave
                         height operational access threshold

    Returns
    -------
    Wbl: Weibull adjustment parameters [x0, b0, k0]
    Tau: Persistence: Mean duration of periods for which Hs<Ha (Hours)
    PT: The probability of occurence of a weather window corresponding to
        sea-state having hs < hs_access_threshold
    Ne: Number of events
    At: Access time (Hours)
    Wt: Waiting time (Hours)
    """

    if hs_access_threshold is None:
        hs_access_threshold = np.linspace(1, 3, 5)

    assert hs.index.is_monotonic_increasing, "hs must be a pandas serie sorted by time"

    nb_years = len(set(hs.index.year))
    nb_hours_by_year = 744
    taui = np.arange(1, nb_hours_by_year + 1)

    hs_this_month = hs.loc[hs.index.month == month]
    duration = len(hs_this_month) / nb_years

    ha_bins, x0, b, k = fit_weibull_distribution(hs_this_month)

    # P is the probability of excedence  P(Hs > Ha)
    P = np.exp(-(((ha_bins - x0) / b) ** k))

    h_mean = b * gamma_function(1 + 1 / k) + x0
    gamma = k + 1.8 * x0 / (h_mean - x0)
    beta = 0.6 * gamma ** 0.287
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
        Pxi = np.exp(-C * xi ** alpha)

        ePa = (hs_threshold - x0) / b
        ePak = ePa ** k
        Pa = np.exp(-ePak)
        PT[ind, :] = Pxi * (1 - Pa)

        # number of events with Hs<Hs and Duration < T - monthly
        number_events[ind, :] = duration * Pxi * (1 - Pa) / taui

    # mean duration of access time - monthly
    number_access_hours = duration * PT

    # mean duration of waiting time - monthly
    waiting_hours = (duration - number_access_hours) / number_events
    number_waiting_hours = np.where(waiting_hours > duration, duration, waiting_hours)

    return [x0, k, b], tau, PT, number_events, number_access_hours, number_waiting_hours


def fit_weibull_distribution(hs: pd.Series) -> [np.array, float, float, float]:
    """Fit a Weibull distribution on Hs.

        The probability of excedence P(Hs > Ha) follows a Weibull distribution
        given by three parameters:

            P(Hs > Ha) = exp(-((Ha - x0)/b)^k)

    Parameters
    ----------
    hs: a pandas Series given the Significant Wave Height (m)
        with a datetime index.

    Returns
    -------
    Ha: np.array: the values for which the distribution has been fitted
    x0: float the parameter of the Weibull distribution
    b: float the parameter of the Weibull distribution
    k: float the parameter of the Weibull distribution
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
    x0 = 0
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

    return bins, x, b, k


if __name__ == "__main__":
    hs = pd.read_csv(
        "../codes_to_migrate/matlab_codes/hs.csv",
        index_col=0,
        parse_dates=True,
    ).hs  # we want a Serie

    hs = hs[hs.index.year < 1997]

    for month in range(1, 13):
        r = compute_weather_windows(hs, month=month)
        (
            [x0, k, b],
            tau,
            PT,
            number_events,
            number_access_hours,
            number_waiting_hours,
        ) = r
