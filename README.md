# Resourcecode library

[![PyPI version](https://badge.fury.io/py/resourcecode.svg)](https://badge.fury.io/py/resourcecode)
[![Status](https://joss.theoj.org/papers/e43574f4a0b6782ee6a112180912dae0/status.svg)](https://joss.theoj.org/papers/e43574f4a0b6782ee6a112180912dae0)
[![Downloads](https://img.shields.io/badge/dynamic/json.svg?label=downloads&url=https%3A%2F%2Fpypistats.org%2Fapi%2Fpackages%2Fresourcecode%2Frecent&query=data.last_month&colorB=brightgreen&suffix=%2FMonth)](https://pypistats.org/packages/2Fresourcecode)

## Description

The `resourcecode` Marine Data Toolbox is a python package  developed within the  **ResourceCODE** project,
to facilitate the access to a recently developed Metocean hindcast
[database](https://www.umr-lops.fr/Donnees/Vagues/sextant#/metadata/d089a801-c853-49bd-9064-dde5808ff8d8),
and to a set of state-of-the-art methods for data analysis. This toolbox provides developers with a set of standard functions
for resource assessment and operations planning.
The advanced statistical modelling tools provided together with the embedded high resolution wave hindcast database allow the
developers with a set of standard functions for resource assessment, extreme values modelling and operations planning.

It is dedicated to users without the knowledge of manipulating numerous netCDF files or developing statistical analysis,
but is also designed to fulfill expert met-ocean analysts needs. The advanced statistical modelling tools provided allow
the developers of Offshore Renewable Energy (**ORE**) devices to conduct the necessary assessments to reduce uncertainty
in expected environmental conditions,and de-risk investment in future technology design.


## Installation

### Dependencies

To install the toolbox, the following packages are necessary:

- python (>= 3.6, <3.12)
- pandas (>= 1.0.0)
- requests (>= 2.23.0)
- numpy (>= 1.20.1)
- scipy (>= 1.6.1)
- pyextremes (>= 2.0.0)
- pytest (>7.0.0)
- pyarrow (>= 6.0.0)
- plotly (>= 4.12.0)
- numexpr (>= 2.7.0)
- xarray (>= 0.19.0)


### Using an environment

Maybe the easiest way to install the toolbox is to create a dedicated virtual
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

In this virtual environment, you can now install the library. The library  is
available on PyPI, and installation is straightforward, using the following
command :

```
(env-resourcecode)$ python -m pip install resourcecode
[…]
```

To test whether the install has been successful, you can run:

```bash
(env-resourcecode)$ python -c "import resourcecode ; print(resourcecode.__version__)"
0.6.0
```

which should print the current locally installed version of `resourcecode`.

## Example of use

Once the library is installed and the configuration is done, you can use the
library.

The first thing to do, is a create a `Client`. The client will query the
Cassandra database for you, and return a pandas dataframe of your selection.

See the following example:

```ipython
>>> import resourcecode
>>> client = resourcecode.Client()
>>> data = client.get_dataframe_from_criteria(
...    """
...    {
...        "node": 42,
...        "start": 1483228400,
...        "end": 1489903600,
...        "parameter": ["fp", "hs"]
...    }
...    """)

>>> data
                        fp     hs
2017-01-01 00:00:00  0.412  0.246
2017-01-01 01:00:00  0.410  0.212
2017-01-01 02:00:00  0.414  0.172
2017-01-01 03:00:00  0.437  0.138
2017-01-01 04:00:00  0.464  0.102
...                    ...    ...
2017-03-19 02:00:00  0.088  0.056
2017-03-19 03:00:00  0.088  0.066
2017-03-19 04:00:00  0.089  0.078
2017-03-19 05:00:00  0.090  0.084
2017-03-19 06:00:00  0.732  0.086
<BLANKLINE>
[1855 rows x 2 columns]

>>> data.describe()
                fp           hs
count  1851.000000  1855.000000
mean      0.260097     0.100231
std       0.233866     0.100087
min       0.050000     0.010000
25%       0.081000     0.028000
50%       0.091000     0.064000
75%       0.463500     0.132000
max       0.877000     0.524000

>>> # if you have matplotlib installed, you can do the following
>>> import pandas as pd
>>> pd.options.plotting.backend = "matplotlib"
>>> ax = data.plot()
>>> ax.figure.savefig('fp_hs.png')

```

which will generate the following plot:

![plot_hs_fp](https://gitlab.ifremer.fr/resourcecode/resourcecode/-/raw/branch/default/fp_hs.png)

## Configuration

The library needs a configuration file to work properly. This file contains in
particular the URL of the Cassandra API to access the hindcast data.

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

## Documentation

We recommend starting with the [official documentation](https://resourcecode.gitlab-pages.ifremer.fr/resourcecode/)
of the toolbox.

For examples of the functionalities offered by the toolbox, some Jupyter notebooks are proposed:

 * [Exploratory Data Analysis](https://nbviewer.org/urls/gitlab.ifremer.fr/resourcecode/tools/producible-estimation-showcase/-/raw/branch/default/index.ipynb)
 * [Extreme Values Analysis](https://nbviewer.org/urls/gitlab.ifremer.fr/resourcecode/tools/extreme-values-analysis/-/raw/branch/default/index.ipynb)
 * [Producible estimation](https://nbviewer.org/urls/gitlab.ifremer.fr/resourcecode/tools/producible-estimation-showcase/-/raw/branch/default/index.ipynb)

# Web portal

The `resourcecode`package goes along with a companion [Web Portal](https://resourcecode.ifremer.fr/resources) that allows to see some of its functionalities in action.

Detailed information about the data availability, tutorials, etc. can be found in the [resources](https://resourcecode.ifremer.fr/resources) page.

Exploration of the hindcast database and some of data exploratory tools are in the [explore](https://resourcecode.ifremer.fr/explore) page.

Both the Jupyter notebook mentioned above and more advanced applications are available as `Jupyter-flex` notebooks. They are
listed on the [Tools](https://resourcecode.ifremer.fr/tools) page.

# Contributing

This package is under active development, and any contribution is welcomed. If you have something
you would like to contribute, but you are not sure how, please don't hesitate to reach out by
sending me an [email](mailto:nicolas.raillard@ifremer.fr) or by
opening an [issue](https://gitlab.ifremer.fr/resourcecode/resourcecode/-/issues). It currently
depends on a registration on the IFREMER Gitlab, which can be done by sending me an email.

## Citing

Please cite it in your publications and do not hesitate to tell your friends and colleagues about it.

```bibtex
@manual{,
  title = {Resourcecode Toolbox},
  author = {Raillard, Nicolas and Chabot, Simon and Maisondieu, Christophe and Darbynian, David and Payne, Gregory and Papillon, Louis},
  url = {https://gitlab.ifremer.fr/resourcecode/resourcecode},
  year = {2022},
  month = {12},
}
```

## Reporting bugs

If you think you found a bug in `resourcecode`, even if you are unsure, please let me know. The
easiest way is to send me an [email](mailto:nicolas.raillard@ifremer.fr) as for the moment submitting issues depends on a registration process mediated by email.

Please try to create a reproducible example with the minimal amount of code required to reproduce the bug you encountered.

## Adding or requesting new functionalities

Whenever possible, we will try to add new functionalities to  `resourcecode` package depending on user's needs and feedbacks.
Proposed functionalities are tracked with issues, so please have a look to see what are the plans.

If you plan to develop new functionalities, you can clone the repository to work on the patch.
Get in touch with the maintainer to refine and prioritize your issue.

If you would like to contribute directly to `resourcecode`, you will have to sign a Contributor License Agreement (CLA).
This CLA allows you to retain your copyright while at the same time it allows us to license `resourcecode` under approved open source license.

CLA documents can be found in the `CLA` folder, both for individuals and entities contributions.

## Licensing

All contributed code will be licensed under a GPL-3 license with authorship attribution. If you did not write the code yourself, it is your responsibility
to ensure that the existing license is compatible and included in the contributed files.

## Code of conduct

Please note that `resourcecode` is released with a [Contributor Code of
Conduct](https://ropensci.org/code-of-conduct/). By contributing to this project
you agree to abide by its terms.

# Acknowledgments

The **ResourceCODE** project, under which this package have been developed,
has received support under the framework of the OCEANERA-NET COFUND project,
with funding provided by national/ regional sources and co-funding by the
European Union's Horizon 2020 research and innovation program.

The partners of the project (EMEC, IFREMER, CentraleNantes, Ocean Data Lab,
Smart Bay Ireland, University College Dublin, INNOSEA and University of Edinburgh)
contributed to this this toolbox and transferred the copyright to IFREMER. They all
agreed to the published License (GPL v3).

The `resourcecode` Python module was developed by [Logilab](https://logilab.fr/)
based on various scientific codes written by the partners of the **ResourceCODE**
project. The copyright have been transferred to IFREMER. More information at https://resourcecode.ifremer.fr.
