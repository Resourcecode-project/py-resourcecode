# coding: utf-8

# Copyright 2020-2022 IFREMER (Brest, FRANCE), all rights reserved.
# contact -- mailto:nicolas.raillard@ifremer.fr
#
# This file is part of Resourcecode.
# Based on a code written by David Darbinyan (david.darbinyan@emec.org.uk)
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
            if pd.Timedelta(nexttime - strtwin) >= dt.timedelta(seconds=3600 * winlen):
                windetect.append(strtwin)
                break
            else:
                thistime = critsubs.index.values[k]
                nexttime = critsubs.index.values[k + 1]
        count += 1
        k = count if not concurrent_windows else k + 1

    return pd.Series(pd.to_datetime(windetect))


def oplen_calc(critsubs, oplen, critical_operation=False, date=1, monstrt=True):
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
    critical_operation : BOOLEAN
        - False for non-critical operations:
          With this flag to False, it is assumed that the operation can be
          halted for the duration of weather downtime and started again
        - True is for continuous window search:
          In this case operations can't be halted and if stopped due to
          weather downtime have to restart from the beginning once the
          conditions allow

        The default is non critical operation.
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

    if monstrt is True:
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
    elif monstrt is False:
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

        stopflg = False
        count = 0
        dur = dt.timedelta(seconds=0)
        while not stopflg:
            if dur >= dt.timedelta(seconds=3600 * oplen):
                stopflg = True
                oplendetect.at[strtime] = critsubs.index[k] - strtime
            else:
                k += 1
            if k >= (critsubs.shape[0] - 1):
                stopflg = True

            if not critical_operation:
                dur = dur + tstep
            else:
                if count > 0 and (critsubs.index[k] - critsubs.index[k - 1]) <= tstep:
                    dur = dur + tstep
                elif count == 0:
                    dur = dur + tstep
                else:
                    dur = dt.timedelta(seconds=0)
                count += 1
    return oplendetect


def wwmonstats(windetect):
    """
    Method to produce monthly statistics of weather windows. Produces plots
    and, optionally, can save the results in csv files

    Parameters
    ----------
    windetect : PANDAS Series
        Series containing the starting dates of weather windows, produced
        using ww_calc method

    Returns
    -------
    wwmonres : PANDAS DATAFRAME
        Returns number of weather window by year/month.

    """
    yeun = windetect.dt.year.unique()
    moun = windetect.dt.month.unique()
    yeun.sort()
    wwmonres = pd.DataFrame(
        np.zeros([yeun.shape[0], moun.shape[0]]), columns=moun, index=yeun
    )

    for ye, mo in product(yeun, moun):
        subs = windetect[(windetect.dt.year == ye) & (windetect.dt.month == mo)]
        wwmonres.at[ye, mo] = subs.shape[0]

    return wwmonres


def olmonstats(oplendetect):
    """
    Method to produce monthly statistics of operational lengths. Produces plots
    and, optionally, can save the results in csv files

    Parameters
    ----------
    oplendetect : PANDAS Series
        Series containing the starting dates and corresponding operational
        lengths, produced using oplen_calc method.

    Returns
    -------
    olmonres : PANDAS DATAFRAME
        Returns operational length in hours by year/month.

    """
    yeun = oplendetect.index.year.unique().to_numpy()
    moun = oplendetect.index.month.unique().to_numpy()

    moun.sort()
    yeun.sort()

    olmonres = pd.DataFrame(
        np.zeros([yeun.shape[0], moun.shape[0]]), columns=moun, index=yeun
    )
    for ye, mo in product(yeun, moun):
        subs = oplendetect[
            (oplendetect.index.year == ye) & (oplendetect.index.month == mo)
        ]
        olmonres.at[ye, mo] = subs[0].days * 24 + subs[0].seconds / 3600
    return olmonres
