#!/usr/bin/env python3
# coding: utf-8

import numpy as np
from resourcecode.utils import zmcomp2metconv


def test_zmcomp2metconv_1():
    u = np.array([1, 0, -1, 0])
    v = np.array([0, 1, 0, -1])

    V_expected = np.array([1, 1, 1, 1])
    D_expected = np.array([270, 180, 90, 0])

    V_got, D_got = zmcomp2metconv(u, v)

    np.testing.assert_array_equal(V_got, V_expected)
    np.testing.assert_array_equal(D_got, D_expected)
