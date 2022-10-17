# coding: utf-8

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
