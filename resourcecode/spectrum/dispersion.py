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

from scipy.constants import g
import numpy as np


def dispersion(
    frequencies: np.ndarray,
    depth: float = float("inf"),
    n_iter: int = 200,
    tol: float = 1e-6,
) -> np.ndarray:
    """Compute the dispersion relation of waves
        Find *k* s.t. (2.pi.f)^2 = g.k.tanh(k.d)

    Parameters
    ----------

    freq:
        the frequency vector
    depth:
        the depth
    n_iter:
        the maximum number of iterations in the non linear solver algorithm.
    tol:
        Tolerance for termination. When tol is specified, the selected
        minimization algorithm sets some relevant solver-specific tolerance(s)
        equal to tol. For detailed control, use solver-specific options.

    Returns
    -------

    out: the wave numbers (same size as freq)

    Example
    -------

    .. doctest:

        >>> import pylab as p
        >>> from resourcecode.spectrum import dispersion
        >>> freq = p.arange(0, 1, 0.01)
        >>> k1 = dispersion(freq, depth=1)
        >>> k10 = dispersion(freq, depth=10)
        >>> kInf = dispersion(freq, depth=float("inf"))
        >>> p.plot(freq, k1)
        >>> p.plot(freq, k10)
        >>> p.plot(freq, kInf)
        >>> p.show()

    """

    frequencies = np.array(frequencies)
    infinite_depth_dispersion = (4 * np.pi**2 / g) * frequencies**2

    if not np.isfinite(depth):
        return infinite_depth_dispersion

    result = np.zeros(len(frequencies))
    for i in range(len(frequencies)):
        if frequencies[i] == 0:
            result[i] = 0
        else:
            c0 = (2 * np.pi * frequencies[i]) ** 2
            k0 = 4.0243 * frequencies[i] ** 2
            xk = k0
            ftest = 99
            for ii in range(n_iter):
                z = xk * depth
                y = np.tanh(z)
                ff = c0 - g * xk * y
                dff = g * (z * (y**2 - 1) - y)
                xk_old = xk
                xk = xk_old - ff / dff
                ftest = abs((xk - xk_old) / xk_old)
                if ftest <= tol:
                    break

            ff = c0 - g * xk * y
            result[i] = xk

    return result
