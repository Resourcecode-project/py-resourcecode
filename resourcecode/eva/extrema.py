# coding: utf-8

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

from typing import Union, List, Collection

import numpy as np
import pandas as pd
from pyextremes import EVA


def get_fitted_models(
    dataframe: pd.DataFrame,
    quantile: float = 0.9,
    r: Union[str, pd.Timedelta] = "0",
) -> List[EVA]:
    models = []
    for var_name, serie in dataframe.items():
        threshold = serie.quantile(quantile)
        model = EVA(serie)
        model.get_extremes(method="POT", threshold=threshold, r=r)
        model.fit_model()
        models.append(model)
    return models


def get_gpd_parameters(fitted_models: Collection[EVA]) -> np.ndarray:
    gpd_param = np.zeros((len(fitted_models), 3))

    for index, model in enumerate(fitted_models):
        threshold = model.extremes_kwargs["threshold"]
        scale = model.model.fit_parameters["scale"]

        # pyextremes will try to find the best model.
        # when 'c' is not specified, it means that 'c' has been fixed to 0.
        shape = model.model.fit_parameters.get("c", 0)

        gpd_param[index, :] = [threshold, scale, shape]

    return gpd_param
