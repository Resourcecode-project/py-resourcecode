#!/usr/bin/env python3
# coding: utf-8

from itertools import product

import numpy as np


def huseby(X, prob, ntheta):
    """Compute the contours of X in the physical space.

    Parameters
    ----------

    X: a numpy array of size [NxM].
       This should be the output of the nataf simulation.
    prob: a numpy array of size [1xN] describing the probability level of the
          contours
    ntheta: the number of angles on [0, 360[, used for the calculation.
            it must be a multiple of 4.

    Returns
    -------

    (X, Y, Z, theta)

    X: a numpy array of size [DxM]
    Y: a numpy array of size [DxM]
    Z: a numpy array of size [DxM]
    theta: a numpy aray of size [DxM]
    """

    # cas sans oversampling
    N, M = X.shape

    assert X.shape[1] == 3, "not handled"
    assert X.shape[1] == len(prob), "not handled"
    assert ntheta % 4 == 0, "ntheta must be a multiple of 4"

    # normalisation
    X_mean = X.mean(axis=0)
    X_std = X.std(axis=0, ddof=1)  # use ddof=1, to have the same output as R
    X = (X - X_mean) / X_std

    Q = (X.T @ X) / (N - 1)
    L = np.linalg.cholesky(Q).T  # use .T as R returned the transposed.
    X = np.linalg.solve(L.T, X.T).T

    # quantiles calculation
    k = N * prob + 0.5
    kf = np.floor(k).astype(int) - 1
    kc = np.ceil(k).astype(int) - 1
    dk = k - kf - 1

    # angles calculation
    theta = np.arange(0, ntheta) * 360 / ntheta * np.pi / 180
    ctheta = np.cos(theta)
    stheta = np.sin(theta)

    C = np.ones((ntheta, ntheta, len(prob)), dtype=float)
    indj = np.hstack(
        (np.arange(0, ntheta / 4 + 1), ntheta - np.arange(1, ntheta / 4 + 1))
    ).astype(int)
    nindj = ntheta / 2 + 1
    ncdir = int(ntheta * nindj)
    cdir = np.zeros((ncdir, M))
    Xres = np.empty((ncdir, M))
    Yres = np.empty((ncdir, M))
    Zres = np.empty((ncdir, M))

    for icdir, (i, j) in enumerate(product(range(ntheta), indj)):
        cdirc = np.array([ctheta[i] * ctheta[j], stheta[j], stheta[i] * ctheta[j]])
        cdir[icdir, :] = cdirc
        Y = X @ cdirc
        Y.sort()
        C[i, j, :] = (Y[kc] - Y[kf]) * dk + Y[kf]

    ps = cdir @ cdir.T
    ps[ps < 0] = 0

    a = np.arange(ntheta / 4 + 1, ntheta - ntheta / 4).astype(int)
    b = np.hstack((np.arange(ntheta / 2, ntheta), np.arange(0, ntheta / 2))).astype(int)
    c = np.hstack(
        (np.arange(ntheta / 4 - 1, -1, -1), ntheta - np.arange(1, ntheta / 4))
    ).astype(int)
    d = ctheta[:, np.newaxis] @ ctheta[np.newaxis, indj]
    e = np.repeat(stheta[indj], ntheta).reshape((-1, ntheta)).T
    f = stheta[:, np.newaxis] @ ctheta[np.newaxis, indj]

    for iprob in range(len(prob)):
        tmp = C[:, indj, iprob].flatten()
        dmin = (tmp / ps).min(axis=1).reshape((-1, len(indj))).T

        # XXX how optimize this loop ?
        for i, index in enumerate(indj):
            C[:, index, iprob] = dmin[i]

        C[:, a, iprob] = C[:, c, iprob][b]

        tmp = d * C[:, indj, iprob]

        Xres[:, iprob] = tmp.T.flat

        tmp = e * C[:, indj, iprob]
        Yres[:, iprob] = tmp.T.flat

        tmp = f * C[:, indj, iprob]
        Zres[:, iprob] = tmp.T.flat

        # Scaling back

        Zres[:, iprob] = (
            L[0, 2] * X_std[2] * Xres[:, iprob]
            + L[1, 2] * X_std[2] * Yres[:, iprob]
            + L[2, 2] * X_std[2] * Zres[:, iprob]
            + X_mean[2]
        )

        Yres[:, iprob] = (
            L[0, 1] * X_std[1] * Xres[:, iprob]
            + L[1, 1] * X_std[1] * Yres[:, iprob]
            + X_mean[1]
        )

        Xres[:, iprob] = L[0, 0] * X_std[0] * Xres[:, iprob] + X_mean[0]

    return Xres, Yres, Zres, theta
