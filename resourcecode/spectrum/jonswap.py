#!/usr/bin/env python3
# coding: utf-8

import numpy as np
import pandas as pd
import numexpr as ne


def jonswap(hs: float, tp: float, gamma: float, freq: np.ndarray) -> np.ndarray:
    """Compute Jonswap spectrum with f (Hz) formulation (Sf = 2*pi*Sw)

    Parameters
    ----------

    hs: m
        Significant wave height
    tp: s
        Peak period
    freq: Hz
        the frequency vector where the spectrum is to be computed
    gamma:
        the peakness factor (e.g. 1 or 3.3)


    Returns
    -------

    out: vector containing the spectrum on input freq
    """

    expr = (
        "5"
        "/ (16 * freq ** 5)"
        "* (hs ** 2)"
        "/ (tp ** 4)"
        "* exp(-5.0 / (4 * tp ** 4) /(freq ** 4))"
        "* gamma ** ("
        "   exp("
        "       -((freq - 1 / tp) ** 2)"
        "       * (tp ** 2)"
        "       / (2 * (where(freq < (1.0 / tp), 0.07, 0.09) ** 2))"
        "   )"
        ")"
    )
    sf = ne.evaluate(expr)
    alpha = (hs ** 2) / (16 * np.trapz(sf, x=freq))
    return alpha * sf


def compute_jonswap_wave_spectrum(
    wave_data: pd.DataFrame, freq: np.ndarray, gamma: float = 1
) -> pd.DataFrame:
    """Computes JONSWAP wave spectrum time series from Hs and Tp time series

    Parameters
    ----------

    wave_data:
        a dataframe with Hs and Tp columns
    freq: Hz
        the frequency vector where the spectrum is to be computed
    gamma:
        the peakness factor (e.g. 1 or 3.3)


    Returns
    -------

    out: dataframe whose columns are the frequency and rows the wave_data datetime index.

        The jonswap spectrum
    """

    def compute_jsonswap_vector(hs, tp):
        return pd.Series(jonswap(hs, tp, gamma=gamma, freq=freq), index=freq)

    spectrum = wave_data.apply(
        lambda x: compute_jsonswap_vector(x["hs"], x["tp"]),
        axis=1,
    )
    return spectrum
