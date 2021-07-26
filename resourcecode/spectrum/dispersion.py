#!/usr/bin/env python3
# coding: utf-8

from scipy.constants import g
import numpy as np


def dispersion(
    frequencies: np.ndarray,
    depth: float = float("inf"),
    n_iter: int = 200,
    dx_rel: float = 1e-6,
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
        the np.maximum np.number of iteration in the Newton-Raphson algorithm.
    dx_rel:
        the np.minimum variation of each step

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

    if not np.isfinite(depth):
        return (4 * np.pi ** 2 / g) * frequencies ** 2

    k = np.empty_like(frequencies)
    for i, fi in enumerate(frequencies):
        if fi == 0:
            k[i] = 0
            continue

        c0 = (2 * np.pi * fi) ** 2
        k0 = 4.0243 * fi ** 2
        xk = k0
        for ii in range(n_iter):
            z = xk * depth
            y = np.tanh(z)
            ff = c0 - g * xk * y
            dff = g * (z * (y ** 2 - 1) - y)
            xk_prev = xk
            xk = xk_prev - ff / dff
            if abs((xk - xk_prev) / xk_prev) <= dx_rel:
                break

        k[i] = xk
    return k
