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

"""
Created on 24/03/2021

@author: Christophe Maisondieu
"""


from resourcecode.weatherwindow.weatherwindow import (
    compute_weather_windows,
    fit_weibull_distribution,
    WeibullDistributionResult,
    WeatherWindowResult,
)

__all__ = [
    "compute_weather_windows",
    "fit_weibull_distribution",
    "WeibullDistributionResult",
    "WeatherWindowResult",
]
