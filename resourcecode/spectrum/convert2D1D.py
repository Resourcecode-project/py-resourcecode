# coding: utf-8

# copyright 2021 IFREMER (Brest, FRANCE), all rights reserved.
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
