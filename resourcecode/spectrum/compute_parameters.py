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
from dataclasses import dataclass, astuple

import numpy as np
import pandas as pd
import xarray
import pytest
from scipy.interpolate import interp1d
from scipy.constants import g

from resourcecode.spectrum.dispersion import dispersion
from resourcecode.spectrum.convert2D1D import raw_convert_spectrum_2Dto1D


@dataclass
class SeaStatesParameters:
    """Describe Sea States Parameters, computed from spectra.

    Parameters
    ----------

    Hm0: m
        Significant wave height from moments
    Tp: s
        Peak Period
    T01: s
        Mean period from moments m0 and m1
    T02: s
        Mean period from moments m0 and m2
    Te: s
        Energy period from moments m-1 and m0
    Mu:
        Spectral bandwitdth parameter
    Nu:
        Spectral bandwidth parameter
    Dm: ° - from
        Mean direction
    Dpm: ° - from
        Mean direction at peak frequency
    Spr:
        Directional Spreading
    CgE: kW/m
        Energy flux (kW/m)
    Km: m⁻¹
        Average wave number
    Lm: m
        Average wavelength
    depth: m
        depth where the spectrum is calculated
    Thetam: 2D only
        Mean direction and directional spreading
    Thetapm: 2D only
        Mean direction at peak frequency
    Spr: 2D only
        Spreading
    Qp: 2D only
        Spectral bandwidth and peakedness parameter (Goba 1970)
    """

    Hm0: float
    Tp: float
    T01: float
    T02: float
    Te: float
    mu: float
    nu: float
    CgE: float
    km: float
    lm: float
    depth: float
    Thetam: Optional[float] = None
    Thetapm: Optional[float] = None
    Spr: Optional[float] = None
    Qp: Optional[float] = None

    # those two methods (iter and len) allows SeaStatesParameters to be compared
    # using pytest.approx
    def __iter__(self):
        return iter(astuple(self))

    def __len__(self):
        return len(astuple(self))

    def approx(self, other):
        return astuple(self) == pytest.approx(astuple(other), rel=1e-5, abs=1e-5)

    def to_dataframe(self):
        """Convert the dataclass to a pandas DataFrame"""
        return pd.DataFrame.from_dict({k: [v] for k, v in self.__dict__.items()})


def raw_compute_parameters_from_1D_spectrum(
    Ef: np.ndarray,
    freq: np.ndarray,
    depth: float = float("inf"),
    water_density: float = 1026,
) -> SeaStatesParameters:
    """
    Compute Sea-States global parameters from 1D (frequency) spectra

    Parameters
    ----------

    Ef:
        the 1D spectrum (freq) at one time step
    freq: Hz
        the frequency vector
    depth: m
        the depth of the water, default to float("inf")
    water_density: kg/m³
        the water density, default to 1025 kg/m³

    Return
    ------

    res: SeaStatesParameters
    """

    # depth must be positive
    if depth <= 0:
        raise ValueError("Depth must be positive")

    # Total energy
    M0 = np.trapz(Ef, x=freq)

    # Significant Wave Height
    Hm0 = 4 * np.sqrt(M0)

    # Periods
    M01 = np.trapz(freq * Ef, x=freq)
    T01 = M0 / M01

    M02 = np.trapz(freq**2 * Ef, x=freq)
    T02 = np.sqrt(M0 / M02)

    Me = np.trapz(Ef / freq, x=freq)
    Te = Me / M0

    # fp evaluaton using spline fitting around Ef peak
    nk = len(freq)
    freqp = interp1d(np.arange(nk), freq)(np.linspace(0, nk - 1, 30 * nk))
    Efp = interp1d(freq, Ef, kind="cubic")(freqp)

    iEfp_max = Efp.argmax()
    fp = freqp[iEfp_max]
    Tp = 1 / fp

    # Spectral Bandwidth and Peakedness parameter (Godo 1970)
    nu = np.sqrt((M0 * M02) / (M01**2) - 1)
    mu = np.sqrt(1 - M01**2 / (M0 * M02))

    k = dispersion(freq, depth, n_iter=200, tol=1e-6)
    kd = k * depth
    km = np.trapz(k * Ef, x=freq) / M0
    lm = 2 * np.pi / km

    # Group velocity
    c1 = 1 + 2 * kd / np.sinh(2 * kd)
    c2 = np.sqrt(g * np.tanh(kd) / k)
    cg = 0.5 * c1 * c2

    # Energy flux
    cgef = np.trapz(cg * Ef, x=freq) / M0
    CgE = water_density * g * cgef

    return SeaStatesParameters(
        Hm0,
        Tp,
        T01,
        T02,
        Te,
        mu,
        nu,
        CgE,
        km,
        lm,
        depth,
    )


def raw_compute_parameters_from_2D_spectrum(
    E: np.ndarray,
    freq: np.ndarray,
    vdir: np.ndarray,
    depth: float = float("inf"),
    water_density: float = 1026,
) -> SeaStatesParameters:
    """
    Compute Sea-States global parameters from 2D (frequency) spectra

    Parameters
    ----------

    E:
        the 2D spectrum (dir, freq) at one time step
    freq: Hz
        the frequency bins vector
    vdir: deg
        the directionnal bins vector
    depth: m
        the water depth, default to float("inf")
    water_density: kg/m³
        the water density, default to 1026 kg/m³

    Return
    ------

    res: SeaStatesParameters
    """

    Ef = raw_convert_spectrum_2Dto1D(E, vdir)
    parameters = raw_compute_parameters_from_1D_spectrum(Ef, freq, depth, water_density)

    # need to convert to radian and order for the remaining calculations
    vd = ((vdir + 180) % 360 * np.pi) / 180
    ivd = vd.argsort()
    E = E[ivd, :]
    vdir = vd[ivd]

    M0 = (parameters.Hm0 / 4) ** 2

    # Energy flux
    k = dispersion(freq, depth, n_iter=200, tol=1e-6)
    kd = k * depth

    if not np.isfinite(depth):
        c1 = 1
    else:
        c1 = 1 + 2 * kd / np.sinh(2 * kd)

    c2 = np.sqrt(g * np.tanh(kd) / k)
    cg = 0.5 * c1 * c2

    # Energy flux
    cgef = np.trapz(cg[:, np.newaxis] * E.T, x=vdir, axis=1)
    parameters.CgE = water_density * g * np.trapz(cgef, x=freq)

    # compute direction from (°)
    aa = (E.T * np.cos(vdir)).T
    bb = (E.T * np.sin(vdir)).T

    af = np.trapz(aa, x=vdir, axis=0)
    am = np.trapz(af, x=freq)

    bf = np.trapz(bb, x=vdir, axis=0)
    bm = np.trapz(bf, x=freq)

    Thetam = (np.arctan2(bm, am) * 180 / np.pi) % 360

    Spr = np.sqrt(2 * (1 - np.sqrt((am**2 + bm**2) / M0**2)))
    Spr = (Spr * 180 / np.pi) % 360

    iEfm = np.trapz(E, x=vdir, axis=0).argmax()
    aap = E[:, iEfm] * np.cos(vdir)
    apm = np.trapz(aap, x=vdir)

    bbp = E[:, iEfm] * np.sin(vdir)
    bpm = np.trapz(bbp, x=vdir)

    # Mean direction at peak frequency
    Thetapm = (np.arctan2(bpm, apm) * 180 / np.pi) % 360

    S2 = E**2
    Qpf = np.trapz((S2 * freq).T, x=vdir)
    MQ = np.trapz(Qpf, x=freq)

    Qp = 2 * MQ / (M0**2)

    parameters.Thetam = Thetam
    parameters.Thetapm = Thetapm
    parameters.Spr = Spr
    parameters.Qp = Qp

    return parameters


def compute_parameters_from_2D_spectrum(
    spectrumDataSet: xarray.Dataset,
    use_depth: bool = True,
) -> pd.DataFrame:
    """
    Compute Sea-States parameters from 2D spectrum time series

    Parameters
    ----------

    spectrumDataSet:
        the spectrum data (as obtained from spec.get_2D_spectrum): a DataSet with time series of spectrum
    use_depth: boolean
        if True, the 'dpt' field is used to compute dispersion relation. Otherwise, infinite depth is assumed.

    Returns
    -------

    xarray.DataArray
         A DataArray with Sea-States parameters
    """
    if use_depth:
        param_xr = xarray.apply_ufunc(
            raw_compute_parameters_from_2D_spectrum,  # first the function
            spectrumDataSet.Ef,  # now arguments in the order expected by 'compute_parameters_from_2D_spectrum'
            spectrumDataSet.frequency,
            spectrumDataSet.direction,
            spectrumDataSet.dpt,
            input_core_dims=[
                ["direction", "frequency"],
                ["frequency"],
                ["direction"],
                [],
            ],  # list with one entry per arg
            output_core_dims=[[]],  # list with one entry per arg
            exclude_dims=set(
                (
                    "frequency",
                    "direction",
                )
            ),
            vectorize=True,  # loop over non-core dims
        )
    else:
        param_xr = xarray.apply_ufunc(
            raw_compute_parameters_from_2D_spectrum,  # first the function
            spectrumDataSet.Ef,  # now arguments in the order expected by 'compute_parameters_from_2D_spectrum'
            spectrumDataSet.frequency,
            spectrumDataSet.direction,
            input_core_dims=[
                ["direction", "frequency"],
                ["frequency"],
                ["direction"],
                [],
            ],  # list with one entry per arg
            output_core_dims=[[]],  # list with one entry per arg
            exclude_dims=set(
                (
                    "frequency",
                    "direction",
                )
            ),
            vectorize=True,  # loop over non-core dims
        )
    sea_state = []
    for d in param_xr.to_dict()["data"]:
        sea_state.append(d.to_dataframe())
    out = pd.concat(sea_state)
    out.insert(0, "time", param_xr.time.values)

    out["depth"] = spectrumDataSet.dpt.values
    out["wnd"] = spectrumDataSet.wnd.values
    out["wnddir"] = spectrumDataSet.wnddir.values
    out["cur"] = spectrumDataSet.cur.values
    out["curdir"] = spectrumDataSet.curdir.values

    return out


def compute_parameters_from_1D_spectrum(
    spectrumDataSet: xarray.Dataset,
    use_depth: bool = True,
) -> pd.DataFrame:
    """
    Compute Sea-States parameters from 1D spectrum time series

    Parameters
    ----------

    spectrumDataSet:
        the spectrum data (as obtained from spec.get_1D_spectrum): a DataSet with time series of spectrum
    use_depth: boolean
        if True, the 'dpt' field is used to compute dispersion relation. Otherwise, infinite depth is assumed.

    Returns
    -------

    xarray.DataArray
         A DataArray with Sea-States parameters

    """
    if use_depth:
        param_xr = xarray.apply_ufunc(
            raw_compute_parameters_from_1D_spectrum,  # first the function
            spectrumDataSet.ef,  # now arguments in the order expected by 'compute_parameters_from_2D_spectrum'
            spectrumDataSet.frequency,
            spectrumDataSet.dpt,
            input_core_dims=[
                ["frequency"],
                ["frequency"],
                [],
            ],  # list with one entry per arg
            output_core_dims=[[]],  # list with one entry per arg
            exclude_dims=set(("frequency",)),
            vectorize=True,  # loop over non-core dims
        )
    else:
        param_xr = xarray.apply_ufunc(
            raw_compute_parameters_from_2D_spectrum,  # first the function
            spectrumDataSet.Ef,  # now arguments in the order expected by 'compute_parameters_from_2D_spectrum'
            spectrumDataSet.frequency,
            input_core_dims=[
                ["frequency"],
                ["frequency"],
                [],
            ],  # list with one entry per arg
            output_core_dims=[[]],  # list with one entry per arg
            exclude_dims=set(("frequency",)),
            vectorize=True,  # loop over non-core dims
        )
    sea_state = []
    for d in param_xr.to_dict()["data"]:
        sea_state.append(d.to_dataframe())
    out = pd.concat(sea_state)
    out.insert(0, "time", param_xr.time.values)

    out["depth"] = spectrumDataSet.dpt.values
    out["wnd"] = spectrumDataSet.wnd.values
    out["wnddir"] = spectrumDataSet.wnddir.values
    out["cur"] = spectrumDataSet.cur.values
    out["curdir"] = spectrumDataSet.curdir.values

    return out
