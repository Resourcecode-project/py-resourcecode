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
The objective is to provide the probability of occurrence and expected
mean number of events of weather windows corresponding to situations when `H_s`
remains below an access threshold (`H_a`) for a given duration. Associated operational
parameters are the access time and waiting time.

Because of the seasonal variability of the wave climate,
Weather Windows parameters are estimated over monthly periods.

The implemented method is based on results presented in:
  - EQUIMAR Deliverable D7.4.1 «Procedures for Estimating Site Accessibility
and Appraisal of Implications of Site Accessibility » (2010),
T. Stallard, University of Manchester, UK,
J-F. Dhedin, Sylvain Saviot and Carlos Noguera, Électricité de France, France.

 - Walker RT, Johanning L, Parkinson R. (2011) Weather Windows for Device Deployment
at UK test Site: Availability and Cost Implications, European Wave and Tidal Energy Conference,
Southampton, EWTEC2011

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
