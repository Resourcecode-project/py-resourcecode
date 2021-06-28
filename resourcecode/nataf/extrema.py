#!/usr/bin/env python3
# coding: utf-8

import numpy as np
import pandas as pd
from pyextremes import EVA


def get_gpd_parameters(dataframe: pd.DataFrame, quantile: float = 0.9) -> np.ndarray:
    gpd_param = np.zeros((dataframe.shape[1], 3))

    for index, (var_name, serie) in enumerate(dataframe.items()):
        threshold = serie.quantile(quantile)

        model = EVA(serie)

        # 'r' is the duration of window used to decluster the exceedances
        # in the R extRemes package, the default value seems to be 0.
        # the default in pyextremes is 24H. It must be a pandas.Timedelta or a
        # string.
        model.get_extremes(method="POT", threshold=threshold, r="0")
        model.fit_model()

        scale = model.model.fit_parameters["scale"]
        # pyextremes will try to find the best model.
        # when 'c' is not specified, it means that 'c' has been fixed to 0.
        shape = model.model.fit_parameters.get("c", 0)

        gpd_param[index, :] = [threshold, scale, shape]

    return gpd_param
