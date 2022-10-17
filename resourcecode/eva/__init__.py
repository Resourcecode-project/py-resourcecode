# coding: utf-8
# Extreme Values Modelling

# Copyright 2020-2022 IFREMER (Brest, FRANCE), all rights reserved.
# contact -- mailto:nicolas.raillard@ifremer.fr
#
# This file is part of Resourcecode.
# Based on a R code written by Nicolas Raillard (nicolas.raillard@ifremer.fr)
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


from resourcecode.eva.censgaussfit import censgaussfit
from resourcecode.eva.extrema import (
    get_fitted_models,
    get_gpd_parameters,
)
from resourcecode.eva.huseby import huseby
from resourcecode.eva.simulation import run_simulation

__all__ = [
    "censgaussfit",
    "get_fitted_models",
    "get_gpd_parameters",
    "huseby",
    "run_simulation",
]
