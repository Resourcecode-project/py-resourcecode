#!/usr/bin/env python3
# coding: utf-8

import numpy as np


def convert_spectrum_2Dto1D(spectrum_2D: np.ndarray, vdir: np.ndarray) -> np.ndarray:
    """
    Converts the 2D spectrum to a 1D spectrum

    Parameters
    ----------

    spectrum_2D:
        the spectrum (dir, freq) at one time step
    vdir:
        direction vector (degree, unsorted)

    Returns
    -------

    spectrum_1D:
        vector with 1D spectrum

    """

    vd = ((vdir + 180) % 360 * np.pi) / 180
    ivd = vd.argsort()
    return np.trapz(spectrum_2D[ivd, :], x=vd[ivd], axis=0)
