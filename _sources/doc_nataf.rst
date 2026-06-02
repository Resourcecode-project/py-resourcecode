Extreme Values Modelling
========================

The objective here is to compute **return level**, which are defined as events
which intensity is exceeded with a given probably. For example, 100-yr return
level are defined as the event that is exceeded *on average* once every hundred
years.

To compute such values, one needs to extrapolate beyond the range of the
observed values. The precise quantification of extreme values relies on the
**Extreme Value Theory** that will not be detailed here (see [1]_ for a details
introduction about the methods).

In this package, we rely on the **Peaks Over Threshold (POT)** approach: the
data above a defined threshold is kept, independent exceedances are identified
based on a time-separation criterion and a **GPD** distribution is fitted to the
set of clusters maxima. The particular case of Exponential distribution is
selected using an AIC criterion.

We also propose in this package to compute multivariate extremes using the
methodology described in [2]_. For the moment, only the Gaussian copula approach
is implemented (a.k.a the Nataf Copula) and fitted on threshold exceedances.
Environmental contours are estimated using the Huseby approach (see [2]_ for
details).

.. [1] Coles, S. (2001). An introduction to statistical modeling of extreme
   values (Vol. 208, p. 208). London: Springer.

.. [2] Raillard Nicolas, Prevosto Marc, Pineau H. (2019). 3-D environmental
   extreme value models for the tension in a mooring line of a semi-submersible.
   Ocean Engineering, 184, 23-31. Publisher's official version :
   https://doi.org/10.1016/j.oceaneng.2019.05.016 , Open Access version :
   https://archimer.ifremer.fr/doc/00498/60948/

.. automodule:: resourcecode.eva
    :members:

