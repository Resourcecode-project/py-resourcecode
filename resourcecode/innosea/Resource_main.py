# -*- coding: utf-8 -*-
# ------------------------------
# Project: Resource Code
# Created by: LPA - INNOSEA
# Date: 14/12/2020
# Modified by:
# ------------------------------


import numpy as np
import matplotlib.pyplot as plt
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

        wave_freq = list(self.freqs)
        capture_width_freq = list(self.capture_width.index)
        if len(wave_freq) != len(capture_width_freq):
            return False
        else:
            for wf, cwf in zip(wave_freq, capture_width_freq):
                if abs(wf - cwf) > tolerance:
                    return True
            return False

    def interp_freq(self):
        """Checks if wave frequency and capture width frequency are the same at a given tolerance.
        If not, interpolates the capture width table"""

        tolerance = 0.001
        if self.is_same_freq(tolerance):
            self.freqs = self.capture_width.index
        else:
            for freq in self.freqs:
                if freq not in self.capture_width.index:
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
        power_list = []
        pto_damp_list = []

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
                np.zeros(len(self.capture_width.columns)),
                index=self.capture_width.columns,
            )
            power_t_no_red = pd.DataFrame(
                np.zeros(len(self.capture_width.columns)),
                index=self.capture_width.columns,
            )
            for pto_t in self.capture_width.columns:
                capt_ratio = self.capture_width[pto_t]
                capt_ratio = capt_ratio[self.freqs]
                # power computation at instant t for each PTO damping
                power_t.loc[pto_t] = (
                    self.rho
                    * self.g
                    * self.width
                    * np.trapz(c_g * self.s.loc[t] * capt_ratio.values, x=self.freqs)
                )
                power_t_no_red.loc[pto_t] = power_t.loc[pto_t]
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
            hs_list.extend([hs])
            tp_list.extend([tp])
            power_list.extend(self.power.loc[t].values)
            pto_damp_list.extend(self.pto_damp.loc[t].values)

        self.freq_data = pd.DataFrame(
            {
                "Hs": hs_list,
                "Tp": tp_list,
                "Power": power_list,
                "PTO damping": pto_damp_list,
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

    def to_csv(self, csv_path):
        """Export computed time series to a csv file

        :param csv_path: output csv file path
        :type csv_path: str"""

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
        df_all_data = pd.DataFrame(all_data, index=self.times, columns=headers)
        df_all_data.to_csv(csv_path)


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


def load_capture_width(capture_width_path, freq_path, pto_data_path):
    """Loads PTO capture width data and stores them in a pandas.DataFrame format,
    with PTO values as columns, frequencies as index.

    :param capture_width_path: capture width csv file path
    :type capture_width_path: str
    :param freq_path: frequencies csv file path
    :type freq_path: str
    :param pto_data_path: PTO values csv file path
    :type pto_data_path: str
    :return: capture width table
    :rtype: pandas.DataFrame"""

    # load WEC capture width
    capture_width = pd.read_csv(capture_width_path, delimiter=",", header=None)
    freq = pd.read_csv(freq_path, delimiter=",", header=None)
    pto_values = pd.read_csv(pto_data_path, delimiter=",", header=None)
    capture_width.columns = pto_values.values.tolist()[0]
    capture_width.index = [val for sublist in freq.values.tolist() for val in sublist]

    return capture_width


def load_hs_tp(wave_file_path):
    """Loads Hs and Tp time series of a csv file, stores it as a pandas.DataFrame

    :param wave_file_path: wave csv file path
    :type wave_file_path: str
    :return: Hs, Tp DataFrame table
    :rtype: pandas.DataFrame"""

    df = pd.read_excel(wave_file_path)
    return df


def create_wave_spectrum(wave_data, freq_vec):
    """Creates JONSWAP wave spectrum time series from Hs and Tp time series

    :param wave_data: Hs, Tp DataFrame table
    :type wave_data: pandas.DataFrame
    :param freq_vec: frequency vector
    :type freq_vec: list, pandas.DataFrame.index
    :return: JONSWAP wave spectrum time series
    :rtype: pandas.DataFrame"""

    spectrum = pd.DataFrame(0, index=wave_data["Var1"], columns=freq_vec)
    for i in range(len(wave_data["Var1"])):
        hs = wave_data["Var2"][i]
        tp = wave_data["Var3"][i]
        # create Jonswap spectrum
        spectrum.iloc[i] = jonswap_f(hs, tp, gamma=1, freq=freq_vec)

    return spectrum


def resource_code_by_spectrum(
    capture_width_path, freq_path, pto_data_path, wave_file_path
):
    """Main functions to load PTO capture width table, wave spectrum time series,
    computes PTO power/damping time series and plots results

    :param capture_width_path: capture width csv file path
    :type capture_width_path: str
    :param freq_path: frequencies csv file path
    :type freq_path: str
    :param pto_data_path: PTO values csv file path
    :type pto_data_path: str
    :param wave_file_path: wave csv file path
    :type wave_file_path: str"""

    # load capture width
    capture_width = load_capture_width(capture_width_path, freq_path, pto_data_path)

    # load Hs/Tp data
    wave_data = load_hs_tp(wave_file_path)

    # create wave spectrum
    # TODO: in the final version, the wave spectrum should be loaded from
    # Resource Code database (Casandra)
    s = create_wave_spectrum(wave_data, capture_width.index)

    # set PTO
    pto = PTO(capture_width, s)

    # plot time series
    plot_time_series(pto)

    # plot cumulative power
    plot_cumulative_power(pto)

    # plot PTO histogram
    plot_pto_hist(pto)

    # show plots
    plt.show()


def plot_time_series(pto):
    """Plot PTO results time series in 3 subplots: wave power, absorbed/mean power
    with/without reduction factor, PTO damping with/without reduction factor.
    Power is converted from W to kW, damping from Ns/m to kNs/m.

    :param pto: PTO object
    :type pto: PTO"""

    # wave power
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))
    ax1.plot(pto.wave_power.div(1000 * pto.width))
    ax1.legend(["Wave power"])
    ax1.grid()
    ax1.set(xlabel="Time", ylabel="Power (kW/m)")
    # absorbed/mean power
    all_time_series = [
        pto.power,
        pto.power_no_red,
        pto.mean_power,
        pto.mean_power_no_red,
    ]
    linestyles = ["solid", "dashed", "solid", "dashed"]
    for time_series, linestyle in zip(all_time_series, linestyles):
        ax2.plot(time_series.div(1000), linestyle=linestyle)
    ax2.legend(
        [
            "Absorbed power (with reduction factor)",
            "Absorbed power (without reduction factor)",
            "Mean power (with reduction factor)",
            "Mean power (without reduction factor)",
        ]
    )
    ax2.grid()
    ax2.set(xlabel="Time", ylabel="Power (kW)")
    # PTO damping
    all_time_series = [pto.pto_damp, pto.pto_damp_no_red]
    for time_series, linestyle in zip(all_time_series, linestyles):
        ax3.plot(time_series.div(1000), linestyle=linestyle)
    ax3.legend(
        [
            "PTO damping (with reduction factor)",
            "PTO damping (without reduction factor)",
        ]
    )
    ax3.grid()
    ax3.set(xlabel="Time", ylabel="Damping (kN.s/m)")


def plot_cumulative_power(pto):
    """Plot PTO cumulative power. Power is converted from W to kW

    :param pto: PTO object
    :type pto: PTO"""

    # absorbed power

    power_kw = pto.power.div(1000)
    # cumulative power
    cumulative_power_kw = pto.cumulative_power
    power_ordered = pto.power.sort_values(by=0)
    index = [x / 1000 for x in power_ordered[0]]
    cumulative_power_kw.index = index
    # mean power
    mean_power_kw = pto.mean_power[0][pto.times[0]] / 1000
    # median power
    median_power_kw = pto.median_power[0][pto.times[0]] / 1000
    # power occurrences, cumulative power, mean and median power
    ax = power_kw.plot.hist(
        bins=len(pto.capture_width.columns) * 5,
        legend=False,
        weights=np.ones_like(power_kw[power_kw.columns[0]]) * 100.0 / len(power_kw),
    )
    ax1 = ax.twinx()
    cumulative_power_kw.plot(ax=ax1, legend=False, color="r")
    ax.grid()
    ax.set_xlabel("WEC Power (kW)")
    ax.set_ylabel("Occurrence (%)")
    ax1.set_ylabel("Normed Cumulative Production (%)")
    line_mean = plt.axvline(x=mean_power_kw, color="y")
    line_median = plt.axvline(x=median_power_kw, color="orange")
    ax.legend([line_mean, line_median], ["Mean power", "Median power"])


def plot_pto_hist(pto):

    pto_damp_kn = pto.pto_damp / 1000
    ax = pto_damp_kn.plot.hist(
        bins=len(pto.capture_width.columns),
        legend=False,
        weights=np.ones_like(pto_damp_kn[pto_damp_kn.columns[0]])
        * 100.0
        / len(pto_damp_kn),
    )
    ax.grid()
    ax.set_xlabel("PTO damping (kN.s/m)")
    ax.set_ylabel("Occurrence (%)")


if __name__ == "__main__":

    capture_width_file = r"Inputs/capture_width.csv"
    freq_file = r"Inputs/Frequencies.csv"
    pto_data_file = r"Inputs/PTO_values.csv"
    wave_file_file = r"Inputs/HsTptimeseries.xlsx"

    resource_code_by_spectrum(
        capture_width_file, freq_file, pto_data_file, wave_file_file
    )
