#!/usr/bin/env python3
# coding: utf-8

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
