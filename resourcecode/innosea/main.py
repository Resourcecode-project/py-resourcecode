# -*- coding: utf-8 -*-
# ------------------------------
# Project: Resource Code
# Created by: LPA - INNOSEA
# Date: 14/12/2020
# Modified by:
# ------------------------------


import numpy as np
import pandas as pd
import math as mt


class PTO:
    """PTO object, storing capture width, wave spectrum, and computing PTO data such as time series
    of wave power, absorbed power, mean power, median power, PTO damping"""

    def __init__(self, capture_width, s):
        self.capture_width = capture_width  # PTO capture width
        self.s = s  # wave spectrum
        self.coef_power_decrement = True  # coefficient to consider power reduction when wave with high steepness # noqa
        self.rho = 1020  # water density (kg/m^3)
        self.g = 9.81  # gravity (m/s^2)
        self.width = 20  # WEC width (m^2)
        self.times = s.index  # time vector
        self.freqs = s.columns  # frequency vector
        # time domain data
        self.power = pd.DataFrame(
            np.zeros(len(self.times)), index=self.times
        )  # absorbed power (W)
        # absorbed power, no reduction (W)
        self.power_no_red = pd.DataFrame(np.zeros(len(self.times)), index=self.times)
        self.mean_power = None  # mean absorbed power (W)
        self.mean_power_no_red = None  # mean absorbed power, no reduction (W)
        self.median_power = None  # median absorbed power (W)
        self.median_power_no_red = None  # median absorbed power, no reduction (W)
        self.wave_power = pd.DataFrame(
            np.zeros(len(self.times)), index=self.times
        )  # incident wave power (W)
        self.pto_damp = pd.DataFrame(
            np.zeros(len(self.times)), index=self.times
        )  # PTO damping (Ns/m)
        # PTO damping, no reduction (Ns/m)
        self.pto_damp_no_red = pd.DataFrame(np.zeros(len(self.times)), index=self.times)
        self.cumulative_power = None  # cumulative power (W)
        # frequency domain data
        self.freq_data = (
            None  # contains Hs, Tp, absorbed power and PTO damping in frequency domain
        )
        # interpolate frequencies (if needed) to match sea-state and PTO capture width data
        self.interp_freq()
        # power computation
        self.get_power_pto_damp()
        # cumulative power
        self.get_cumulative_power()

    def is_same_freq(self, tolerance):
        """Checks if wave frequency and capture width frequency are the same at a given tolerance

        :param tolerance: tolerance
        :type tolerance: float
        :return: True if same frequency vector (if everything under tolerance), else return False
        :rtype: bool"""

        wave_freq = self.freqs.to_numpy()
        capture_width_freq = self.capture_width.index.to_numpy()
        if len(wave_freq) != len(capture_width_freq):
            return False
        else:
            return abs(wave_freq - capture_width_freq).max() > tolerance

    def interp_freq(self):
        """Checks if wave frequency and capture width frequency are the same at a given tolerance.
        If not, interpolates the capture width table"""

        known_freqs = set(self.capture_width.index)
        tolerance = 0.001
        if self.is_same_freq(tolerance):
            self.freqs = self.capture_width.index
        else:
            for freq in self.freqs:
                if freq in known_freqs:
                    continue

                known_freqs.add(freq)
                self.capture_width = self.capture_width.append(
                    pd.Series(name=freq, dtype="float64")
                )
                self.capture_width.sort_index(inplace=True)
                self.capture_width = self.capture_width.interpolate()

    def get_power_pto_damp(self):
        """Compute absorbed power, mean power, median power, PTO damping time series"""

        # frequency domain data
        hs_list = []
        tp_list = []

        for t in self.times:
            # Hs, Tp conditions
            m_m1 = self.compute_spectrum_moment(self.freqs, self.s.loc[t], n=-1)
            m_0 = self.compute_spectrum_moment(self.freqs, self.s.loc[t], n=0)
            m_2 = self.compute_spectrum_moment(self.freqs, self.s.loc[t], n=2)
            hs = 4 * np.sqrt(m_0)
            te = m_m1 / m_0
            tz = np.sqrt(m_0 / m_2)
            gamma = 1  # assumption
            tp = te * 1.16637561872 * gamma ** -0.0433388762904
            # sea-state steepness computation
            if self.coef_power_decrement:
                s_s = 2.0 * np.pi * hs / (self.g * tz ** 2)
            else:
                s_s = 0
            # group velocity
            # infinite depth assumption
            c_g = (self.g / (4 * mt.pi)) / self.freqs
            power_t = pd.DataFrame(
                [
                    self.rho
                    * self.g
                    * self.width
                    * np.trapz(
                        c_g * self.s.loc[t] * cw_column,
                        x=self.freqs,
                    )
                    for cw_column in self.capture_width
                ],
                index=self.capture_width.columns,
            )
            power_t_no_red = power_t.copy()
            if np.logical_and(self.coef_power_decrement, s_s > 0.02):
                # estimate new decreased capture width ratio
                coef = np.cos(np.pi * (s_s - 0.02) / 0.36) ** 2.0
                # get new power estimate
                power_t = power_t.mul(coef)
            # safety mode, no power absorbed
            elif s_s > 0.1:
                power_t = 0
            # PTO damping chosen for best power capture
            # (including reduction capture if wave steepness too high)
            pto_opt = power_t.idxmax()
            self.pto_damp.loc[t] = pto_opt
            self.power.loc[t] = power_t.loc[pto_opt.values].values
            # PTO damping chosen for best power capture (without reduction)
            pto_opt_no_red = power_t_no_red.idxmax()
            self.pto_damp_no_red.loc[t] = pto_opt_no_red
            self.power_no_red.loc[t] = power_t_no_red.loc[pto_opt_no_red.values].values
            # wave power computation
            self.wave_power.loc[t] = (
                self.rho
                * self.g
                * self.width
                * np.trapz(c_g * self.s.loc[t], x=self.freqs)
            )
            # frequency domain data
            hs_list.append(hs)
            tp_list.append(tp)

        self.freq_data = pd.DataFrame(
            {
                "Hs": hs_list,
                "Tp": tp_list,
                "Power": self.power.values.flatten(),
                "PTO damping": self.pto_damp.values.flatten(),
            }
        )
        self.mean_power = pd.DataFrame(
            data=self.power.mean()[0] * np.ones(len(self.times)), index=self.times
        )
        self.mean_power_no_red = pd.DataFrame(
            data=self.power_no_red.mean()[0] * np.ones(len(self.times)),
            index=self.times,
        )
        self.median_power = pd.DataFrame(
            data=self.power.median()[0] * np.ones(len(self.times)), index=self.times
        )
        self.median_power_no_red = pd.DataFrame(
            data=self.power_no_red.median()[0] * np.ones(len(self.times)),
            index=self.times,
        )

    def get_cumulative_power(self):
        """Compute PTO cumulative power"""

        power_ordered = self.power.sort_values(by=0)
        self.cumulative_power = pd.DataFrame(
            data=100 * power_ordered.cumsum() / power_ordered.sum()
        )

    @staticmethod
    def compute_spectrum_moment(f, s, n=0):
        """Computes n-th moment of a spectrum

        :param f: frequency values
        :type f: numpy.array
        :param s: wave spectrum
        :type s: numpy.array
        :param n: moment order
        :type n: int
        :return: moment value
        :rtype: float"""

        fmin = np.min(f)
        fmax = np.max(f)
        nf0 = 600
        f0 = np.linspace(fmin, fmax, nf0)
        s0 = np.interp(f0, f, s)

        fn = np.power(f0, n)
        mn = np.trapz(s0 * fn, x=f0)

        return mn

    def to_dataframe(self):
        headers = [
            "Wave power",
            "Absorbed power (with reduction factor)",
            "Absorbed power (without reduction factor)",
            "Mean power (with reduction factor)",
            "Mean power (without reduction factor)",
            "Median power (with reduction factor)",
            "Median power (without reduction factor)",
            "PTO damping (with reduction factor)",
            "PTO damping (without reduction factor)",
        ]
        all_data = np.stack(
            (
                self.wave_power[0],
                self.power[0],
                self.power_no_red[0],
                self.median_power[0],
                self.median_power_no_red[0],
                self.mean_power[0],
                self.mean_power_no_red[0],
                self.pto_damp[0],
                self.pto_damp_no_red[0],
            )
        ).transpose()
        return pd.DataFrame(all_data, index=self.times, columns=headers)

    def to_csv(self, csv_path):
        """Export computed time series to a csv file

        :param csv_path: output csv file path
        :type csv_path: str"""

        self.to_dataframe().to_csv(csv_path)


def jonswap_f(hs, tp, gamma, freq):
    """Compute Jonswap spectrum with f (Hz) formulation (Sf = 2*pi*Sw)

    :param hs: Significant wave height (m)
    :type hs: float
    :param tp: Peak period (s)
    :type tp: float
    :param gamma: peakness factor (e.g. 1 or 3.3)
    :type gamma: float
    :param freq: vector of frequency where the spectrum is to be computed
    :type freq: numpy.array
    :return: vector containing the spectrum on input freq
    :rtype: numpy.array"""

    hs = float(hs)
    tp = float(tp)
    gamma = float(gamma)

    fp = 1.0 / tp
    sigma = 0.07 * (freq < fp) + 0.09 * (freq >= fp)
    sf = (
        5
        / (16 * freq ** 5)
        * (hs ** 2)
        / (tp ** 4)
        * np.exp(-5.0 / (4 * tp ** 4) / (freq ** 4))
        * gamma ** (np.exp(-((freq - 1 / tp) ** 2) * (tp ** 2) / (2 * (sigma ** 2))))
    )
    alpha = (hs ** 2) / (16 * np.trapz(sf, x=freq))
    sf = alpha * sf

    return sf


def create_wave_spectrum(wave_data, freq_vec):
    """Creates JONSWAP wave spectrum time series from Hs and Tp time series

    :param wave_data: Hs, Tp DataFrame table
    :type wave_data: pandas.DataFrame
    :param freq_vec: frequency vector
    :type freq_vec: list, pandas.DataFrame.index
    :return: JONSWAP wave spectrum time series
    :rtype: pandas.DataFrame"""

    def create_jsonswap_vector(hs, tp):
        return jonswap_f(hs, tp, gamma=1, freq=freq_vec)

    spectrum = wave_data.apply(
        lambda x: pd.Series(create_jsonswap_vector(x["hs"], x["tp"]), index=freq_vec),
        axis=1,
    )
    return spectrum
