# -*- coding: utf-8 -*-
"""
Operational Planning module

Module to support operational planning
The module allows calculating statistics of number of weather windows and/or
statistics of length of operations, when accounting for weather downtime

In this module weather window is defined as uninterrupted window of given
length, when the operational critera are met. The main deliverable is the
number (count) of weather windows (and various statistics around the number).
The number of weather windows for a given period of time can be considered
back-to-back (next window is considered after the end of pervious window)
or for any timestamp - every timestamop is considered as potential start
of a weather window

The operational length is how long will it take to carry out the operation of
given nominal length, when taking into account weather downtime. Operational
length is provided in units of time. When calculating the length, operations
can be considered critical or non-critical. With critical operations, the
full operations have to restart if criteria is exceeded. With non-critical
operations, they can be paused for the bad weather and continued once the
conditions meet the criteria

The module, in order of execution to produce a full result, consists of:

1. Use a pandas query to limit the dataset to the timestamps matching
   operational criteria (`data.query("hs < 2 and tp < 3")` for instance)
2. ww_calc - method to identify the weather windows
3. oplen_calc - method to calculate operational length
4. wwmonstats - method that produces monthly statistics of number of
   weather windows
5. olmonstats - method that produces monthly statistics of operational
   length values

IMPORTANT: read_data_temp - is a temporary method to be replaced by method to
export the data directly from Casandra

Created on Wed Dec  2 14:14:48 2020
@author: david.darbinyan
"""
from itertools import product

import pandas as pd
import datetime as dt
import numpy as np


def _get_timestep(data: pd.DataFrame) -> pd.Timedelta:
    """
    Compute the data timestep, estimated using either:
    - dataframe built-in methods
    - directly as difference between the timestamps

    Parameters
    ----------

    data:
        a dataframe resulting from the resourcode Client, with a
        DateTimeIndex.

    Returns
    -------

    dt:
        the estimated timestep
    """

    tsfrq = data.index.inferred_freq
    if tsfrq is None:
        tsdif = data.index.to_series().diff().abs()
        tstep = tsdif[tsdif != dt.timedelta(0)].min()
    else:
        tstep = pd.to_timedelta(pd.tseries.frequencies.to_offset(tsfrq))
    return tstep


def ww_calc(
    critsubs: pd.DataFrame, winlen: float, concurrent_windows: bool = True
) -> pd.Series:
    """
    Method that calculates and returns start date of each weather window

    Parameters
    ----------
    critsubs : PANDAS DATAFRAME
        Subset of original dataset containing only data that meets the
        criteria
    winlen : float
        Length of the weather window in hours
    concurrent_windows: bool
        If True, the algorithm searches for window, if a window is found,
        search of next window will start from the end of the previous window.

        If False, it uses continuous window search:
            The algorithm searches for window starting from every time step
            that meets the criteria.

    Returns
    -------
    windetect : PANDAS Series
        Series containing the starting dates of weather windows

    """
    windetect = []
    tstep = _get_timestep(critsubs)
    if concurrent_windows:  # back-to-back windows
        k = 0
        while k < (critsubs.shape[0] - 2):
            strtwin = critsubs.index.values[k]
            thistime = strtwin
            nexttime = critsubs.index.values[k + 1]
            while pd.Timedelta(nexttime - thistime) <= tstep and k < (
                critsubs.shape[0] - 2
            ):
                k += 1
                if pd.Timedelta(nexttime - strtwin) >= dt.timedelta(
                    seconds=3600 * winlen
                ):
                    windetect.append(strtwin)
                    break
                else:
                    thistime = critsubs.index.values[k]
                    nexttime = critsubs.index.values[k + 1]
            k += 1
    else:  # any start time
        k = 0
        count = 0
        while k < (critsubs.shape[0] - 2):
            strtwin = critsubs.index.values[k]
            thistime = strtwin
            nexttime = critsubs.index.values[k + 1]
            while pd.Timedelta(nexttime - thistime) <= tstep and k < (
                critsubs.shape[0] - 2
            ):
                k += 1
                if pd.Timedelta(nexttime - strtwin) >= dt.timedelta(
                    seconds=3600 * winlen
                ):
                    windetect.append(strtwin)
                    break
                else:
                    thistime = critsubs.index.values[k]
                    nexttime = critsubs.index.values[k + 1]
            count += 1
            k = count

    return pd.Series(windetect)


def oplen_calc(critsubs, oplen, flag=0, date=1, monstrt=True):
    """
    Method for calculating length of operations when taking into account the
    weather downtime. The operational length is calculated for a given starting
    date

    Parameters
    ----------

    critsubs : PANDAS DATAFRAME
        Subset of original dataset containing only data that meets the
        criteria
    oplen : DOUBLE
        Nominal length of the operation (if no downtime), in hours
    flag : INT,DOUBLE
        Flag having value 0 or 1.

        - Flag 0 is for non-critical operations:
          With this flag it is assumed that the operation can be halted
          for the duration of weather downtime and started again
        - Flag 1 is for continuous window search:
          In this case operations can't be halted and if stopped due to
          weather downtime have to restart from the beginning once the
          conditions allow

        The default is 0.
    date : INT,DATETIME optional
        If the method is used for one off operational length calulation
        (see monstrt) the start date in DATETIME format should be defined
        If the method is used for producing a monthly statistics of operational
        lengths for opearations starting on the day of month defined as integer
        in date parameter. The default is 1 (with default monstrt = True)
    monstrt : BOOLEAN, optional
        Calculate operational lengths for monthly start dates or for a specific
        date. If monstrt is True, the method will take start day from 'date'
        parameter and calculate operational lengths for each month starting
        at the provided day. If it is Flase, the operational length will be
        calculated for a single start date provided by 'date' parameter.
        The default is True.

    Raises
    ------
    NameError
        Errors if the data types don't match.

    Returns
    -------
    oplendetect : PANDAS Series
        Output pandas series where indexes reflect the start date of the
        operation and the OpLengthHrs column shows the length of the
        operations in Timedelta format.

    """
    tstep = _get_timestep(critsubs)

    if monstrt and isinstance(monstrt, bool):
        if isinstance(date, dt.datetime):
            dayval = date.day
        elif isinstance(date, int) and date >= 1:
            dayval = date
        else:
            msg = (
                "Variable date in monthly results calculation should be"
                " positive integer or datetime object"
            )
            raise NameError(msg)
        yerng = [min(critsubs.index).year, max(critsubs.index).year]
        morng = [min(critsubs.index).month, max(critsubs.index).month]
        daterng = pd.date_range(
            start=dt.datetime(yerng[0], morng[0], 1),
            end=dt.datetime(yerng[1], morng[1], 1),
            freq="MS",
        )
        daterng = daterng.shift(dayval - 1, freq="D")
        oplendetect = pd.Series(
            np.zeros(daterng.shape[0], dtype="timedelta64[s]"), index=daterng
        )
    elif not (monstrt) and isinstance(monstrt, bool):
        if isinstance(date, dt.datetime):
            daterng = pd.date_range(start=date, end=date)
            oplendetect = pd.Series(
                np.zeros(daterng.shape[0], dtype="timedelta64[s]"), index=daterng
            )
        else:
            msg = (
                "Variable date in single result calculation should be"
                " a datetime object"
            )
            raise NameError(msg)
    else:
        raise NameError("Input option monstrt should be boolean")

    for strtime in oplendetect.index:
        if critsubs.index.max() >= strtime:
            k = critsubs.index.get_loc(critsubs.index[critsubs.index >= strtime].min())
        else:
            break
        stopflg = 0
        dur = dt.timedelta(seconds=0)
        if flag == 0:  # non-critical
            while stopflg == 0:
                if dur >= dt.timedelta(seconds=3600 * oplen):
                    stopflg = 1
                    oplendetect.at[strtime] = critsubs.index[k] - strtime
                else:
                    k += 1
                if k >= (critsubs.shape[0] - 1):
                    stopflg = 1
                dur = dur + tstep

        elif flag == 1:  # critical ops
            count = 0
            while stopflg == 0:
                if dur >= dt.timedelta(seconds=3600 * oplen):
                    stopflg = 1
                    oplendetect.at[strtime] = critsubs.index[k] - strtime
                else:
                    k += 1
                if k >= (critsubs.shape[0] - 1):
                    stopflg = 1

                if count > 0 and (critsubs.index[k] - critsubs.index[k - 1]) <= tstep:
                    dur = dur + tstep
                elif count == 0:
                    dur = dur + tstep
                else:
                    dur = dt.timedelta(seconds=0)

                count += 1
        else:
            raise NameError("Flag value should be 0 or 1")
    return oplendetect


def wwmonstats(windetect, fileall=None, filestats=None):
    """
    Method to produce monthly statistics of weather windows. Produces plots
    and, optionally, can save the results in csv files

    Parameters
    ----------
    windetect : PANDAS Series
        Series containing the starting dates of weather windows, produced
        using ww_calc method
    fileall : STRING, optional
        Full path name to file where the number of weather windows by month
        and year are saved on csv format. The default is None (don't save)
    filestats : STRING, optional
        Full path name to file where the monthly statistics of weather windows
        are saved in csv format. The default is None (don't save)

    Returns
    -------
    wwmonres : PANDAS DATAFRAME
        Returns number of weather window by year/month.

    """
    yeun = windetect.dt.year.unique()
    moun = windetect.dt.month.unique()
    yeun.sort()
    moun.sort()
    prcntl = [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
    wwmonres = pd.DataFrame(
        np.zeros([yeun.shape[0], moun.shape[0]]), columns=moun, index=yeun
    )

    for ye, mo in product(yeun, moun):
        subs = windetect[(windetect.dt.year == ye) & (windetect.dt.month == mo)]
        wwmonres.at[ye, mo] = subs.shape[0]

    stats = wwmonres.describe(percentiles=prcntl)
    if fileall is not None:
        wwmonres.to_csv(
            fileall, index=True, index_label="Year", header=True, float_format="%.1f"
        )
    if filestats is not None:
        stats.to_csv(
            filestats, index=True, float_format="%.3f", index_label="Stats", header=True
        )

    pltst = stats.transpose().plot()
    pltst.set_xlabel("Month")
    pltst.set_ylabel("Number of Weather Windows")
    pltal = wwmonres.plot()
    pltal.set_xlabel("Year")
    pltal.set_ylabel("Number of Weather Windows")
    return wwmonres


def olmonstats(oplendetect, fileall=None, filestats=None):
    """
    Method to produce monthly statistics of operational lengths. Produces plots
    and, optionally, can save the results in csv files

    Parameters
    ----------
    oplendetect : PANDAS Series
        Series containing the starting dates and corresponding operational
        lengths, produced using oplen_calc method.
    fileall : STRING, optional
        Full path name to file where the operational length by month
        and year are saved in csv format. The default is None (don't save)
    filestats : STRING, optional
        Full path name to file where the monthly statistics of operational
        length are saved in csv format. The default is None (don't save)

    Returns
    -------
    olmonres : PANDAS DATAFRAME
        Returns operational length in hours by year/month.

    """
    yeun = oplendetect.index.year.unique().to_numpy()
    moun = oplendetect.index.month.unique().to_numpy()

    moun.sort()
    yeun.sort()

    prcntl = [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
    olmonres = pd.DataFrame(
        np.zeros([yeun.shape[0], moun.shape[0]]), columns=moun, index=yeun
    )
    for ye, mo in product(yeun, moun):
        subs = oplendetect[
            np.array(
                [
                    oplendetect.index.year == ye,
                    oplendetect.index.month == mo,
                ]
            ).all(axis=0)
        ]
        olmonres.at[ye, mo] = subs[0].days * 24 + subs[0].seconds / 3600

    stats = olmonres.describe(percentiles=prcntl)
    if fileall is not None:
        olmonres.to_csv(
            fileall, index=True, index_label="Year", header=True, float_format="%.1f"
        )
    if filestats is not None:
        stats.to_csv(
            filestats, index=True, float_format="%.3f", index_label="Stats", header=True
        )

    pltst = stats.transpose().plot()
    pltst.set_xlabel("Month")
    pltst.set_ylabel("Operational Length [hrs]")
    pltal = olmonres.plot()
    pltal.set_xlabel("Year")
    pltal.set_ylabel("Operational Length [hrs]")
    return olmonres
