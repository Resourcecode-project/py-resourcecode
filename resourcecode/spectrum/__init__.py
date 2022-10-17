# coding: utf-8
# Spectral data tools

# Copyright 2020-2022 IFREMER (Brest, FRANCE), all rights reserved.
# contact -- mailto:nicolas.raillard@ifremer.fr
#
# This file is part of Resourcecode.
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

from resourcecode.spectrum.jonswap import compute_jonswap_wave_spectrum

from resourcecode.spectrum.convert2D1D import raw_convert_spectrum_2Dto1D
from resourcecode.spectrum.convert2D1D import convert_spectrum_2Dto1D
from resourcecode.spectrum.dispersion import dispersion
from resourcecode.spectrum.compute_parameters import (
    raw_compute_parameters_from_1D_spectrum,
    raw_compute_parameters_from_2D_spectrum,
    compute_parameters_from_1D_spectrum,
    compute_parameters_from_2D_spectrum,
)
from resourcecode.spectrum.download_data import get_2D_spectrum
from resourcecode.spectrum.download_data import get_1D_spectrum

from resourcecode.spectrum.plots import plot_2D_spectrum
from resourcecode.spectrum.plots import plot_1D_spectrum

__all__ = [
    "SeaStatesParameters",
    "compute_jonswap_wave_spectrum",
    "raw_compute_parameters_from_1D_spectrum",
    "raw_compute_parameters_from_2D_spectrum",
    "compute_parameters_from_1D_spectrum",
    "compute_parameters_from_2D_spectrum",
    "raw_convert_spectrum_2Dto1D",
    "convert_spectrum_2Dto1D",
    "dispersion",
    "get_2D_spectrum",
    "get_1D_spectrum",
    "plot_2D_spectrum",
    "plot_1D_spectrum",
]
