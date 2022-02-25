# Resourcecode library

## Description

The **ResourceCODE** Marine Data Toolbox is a python package to facilitate the access to recent hindcast database of sea-state,
along with a set of state-of-the-art methods for data analysis. This toolbox provides developers with a set of standard functions
for resource assessment and operations planning.
The advanced statistical modelling tools provided together with the embedded high resolution wave hindcast database allow the
developers with a set of standard functions for resource assessment, extreme values modelling and operations planning.

It is dedicated to users without the knowledge of manipulating numerous netCDF files or developing statistical analysis,
but is also designed to fulfill expert met-ocean analysts needs. The advanced statistical modelling tools provided allow
the developers of Offshore Renewable Energy (**ORE**) devices to conduct the necessary assessments to reduce uncertainty
in expected environmental conditions,and de-risk investment in future technology design.


## Installation

To install the library, you may first of all, create a dedicated virtual
environment:

```shell
$ cd /your/work/directory
$ python3 -m venv env-resourcecode
```

then, you activate it:

```shell
$ source env-resourcecode/bin/activate
(env-resourcecode)$
```

In this virtual environment, you can now install the library. The library is not
available on PyPI yet, therefore you have to download the archive
([here](https://forge.extranet.logilab.fr/ifremer/resourcecode/-/archive/branch/default/resourcecode-branch-default.zip)
for instance), and then install it:

```
(env-resourcecode)$ python -m pip install /your/downloads/directory/resourcecode-branch-default.zip
[…]
```

To test whether the install has been successful, you can run:

```bash
(env-resourcecode)$ python -c "import resourcecode ; print(resourcecode.__version__)"
0.1.0
```

which should print the current locally installed version of `resourcecode`.


## Configuration

The library needs a configuration file to work properly. This file contains in
particular the URL of the Cassendra API.

The library will look for the configuration at the following location (in the
order) :

* in the file described by the `RESOURCECODE_CONFIG_FILEPATH` environment
  variable.
* in a file named `resourcecode.ini` in the current directory.
* in a file located in `$HOME/.config/resourcecode.ini`.
* in a file located in `/usr/local/etc/resourcecode/config.ini`

The search stops at the first file found.

The default configuration file can be found [here](./config/config.ini). You may
download it and move it to this location: `$HOME/.config/resourcecode.ini`.

You may need to update the Cassandra URL.

## Example of use

Once the library is installed and the configuration is done, you can use the
library.

The first thing to do, is a create a `Client`. The client will query the
cassandra database for you, and return a pandas dataframe of your selection.

See the following example:

```ipython
>>> import resourcecode
>>> client = resourcecode.Client()
>>> data = client.get_dataframe_from_criteria(
"""
{
    "node": 0,
    "start": 1483228400,
    "end": 1489903600,
    "parameter": ["fp", "hs"]
}
""")
>>> data
                        fp     hs
2017-01-01 00:00:00  0.074  0.296
2017-01-01 01:00:00  0.072  0.400
2017-01-01 02:00:00  0.071  0.356
2017-01-01 03:00:00  0.071  0.350
2017-01-01 04:00:00  0.074  0.256
...                    ...    ...
2017-01-31 19:00:00  0.096  0.250
2017-01-31 20:00:00  0.096  0.332
2017-01-31 21:00:00  0.096  0.480
2017-01-31 22:00:00  0.096  0.612
2017-01-31 23:00:00  0.097  0.756

[744 rows x 2 columns]
>>> data.describe()
               fp          hs
count  744.000000  744.000000
mean     0.088046    0.537551
std      0.011400    0.192594
min      0.058000    0.160000
25%      0.081000    0.370000
50%      0.087000    0.533000
75%      0.095000    0.688500
max      0.120000    0.948000

>>> # if you have malptolib installed, you can do the following
>>> ax = data.plot()
>>> ax.figure.savefig('fp_hs.png')
```

which will generate the following plot:

![plot_hs_fp](https://gitlab.ifremer.fr/resourcecode/resourcecode/-/raw/branch/default/fp_hs.png)


# Acknowledgments

The ResourceCode Python module was developed by [Logilab](https://logilab.fr/)
based on various scientific codes written by the partners of the ResourceCode
Projet: EMEC, CentraleNantes, Ocean Data Lab, Smart Bay Ireland, University
College Dublin, INNOSEA, Ifremer, University of Edinburgh. More information at
https://resourcecode.ifremer.fr.
