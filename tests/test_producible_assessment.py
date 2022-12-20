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

import pandas as pd
from pathlib import Path
import pytest

from resourcecode import producible_assessment
from resourcecode.spectrum import compute_jonswap_wave_spectrum


def test_producible_assessment():
    INNOSEA_DATA_DIR = Path(producible_assessment.__file__).parent / "Inputs"
    capture_width_path = INNOSEA_DATA_DIR / "capture_width.csv"
    freq_path = INNOSEA_DATA_DIR / "Frequencies.csv"
    pto_data_path = INNOSEA_DATA_DIR / "PTO_values.csv"
    hs_tp_input_path = INNOSEA_DATA_DIR / "HsTptimeseries.csv"

    capture_width = pd.read_csv(capture_width_path, delimiter=",", header=None)
    freq = pd.read_csv(freq_path, delimiter=",", header=None)
    pto_values = pd.read_csv(pto_data_path, delimiter=",", header=None)
    capture_width.columns = pto_values.values.tolist()[0]
    capture_width.index = [val for sublist in freq.values.tolist() for val in sublist]
    wave_data = pd.read_csv(hs_tp_input_path, delimiter=",", index_col="time", header=0)

    freq_vec = capture_width.index
    spectrum = compute_jonswap_wave_spectrum(wave_data, freq_vec)

    pto = producible_assessment.PTO(capture_width, spectrum)
    assert len(pto.freq_data) == len(wave_data)
    assert pto.width == 20
    assert pto.wave_power[0][0] == pytest.approx(29315.1936)
    assert pto.wave_power[0][-1] == pytest.approx(431472.6246)
