## Version 0.5.5 (2022-02-25)
### 👷 Bug fixes

 - Add some control on inputs in functions (fixed: #5, #6, #7) 

### 📝 Documentation

- Update documentation due to the release on pypi (fixed: #3)
- Update documentation for the producible estmation module
- Correct some typos (fixed: #4)

### 🤖 Continuous integration

- CI/CD to automate release to pypi is functionnal

## Version 0.5.4 (2022-02-24)
### 📝 Documentation

- Release to pipy

## Version 0.5.3 (2022-02-24)
### 📝 Documentation

- Change LISENSE to GPL v3 and later

## Version 0.5.2 (2021-11-24)
### 👷 Bug fixes

- fix an issue in which the node extracted from Casandra was not the right one

### 📝 Documentation

- Add LISENSE file
- Add CITATION.cff to ease citation of the package

## Version 0.5.1 (2021-10-28)
### 👷 Bug fixes

- fix typo in 'producible_assessment' module name

### 📝 Documentation

- add doc for producible assessment
- fix documentation link for EVA

## Version 0.5.0 (2021-10-28)
### 📝 Documentation

- add acknowledgements to logilab
- ask to contact N. Raillard for tokens and replace logilab's forge by ifremer's one

### 🤖 Continuous integration

- refactor gitlab-ci-ifremer not to be dependant of logilab


## Version 0.4.0 (2021-10-15)
### 🎉 New features

- add a utils function to convert wind/zonal velocity to magnitude and direction of speed (#26)
- export get_closest_point and get_closest_station at the root of the module
- netcfd: add to helpers to read from / export to netcfd (#25)
- opsplanning: add the code and the doc
- resassess: add the code and the doc
- theme: add a plotly theme to embed a resourcecode watermark and use it by default

### 👷 Bug fixes

- innosea: the optimisation done in c20b0a6ba was a bit to much
- opsplanning: make sure windetect is returned as a pandas datetime series
- typo: rename netcfd to netcdf

### 📝 Documentation

- nataf: add a documentation about nataf
- opsplanning: add the auto doc

### 🤖 Continuous integration

- add a gitlab-ci for ifremer runners
- use python3.9

## Version 0.3.0 (2021-09-03)
### 🎉 New features

- client: add the possibility to query the tp parameter
- client: add a method to get dataframe from the selection URL (#9)
- client: add a method to get the datetime from an explicit data selection (#9)
- client: allow criteria to be a dictionnary or a string (#9)
- client: print a message and return an empty dataframe when the API fails
- client: tolerates "paramaters" and "parameter" in the criteria
- client: use default parameters for node and start/stop datetime if there are not present (#22)
- client: raise an exception if one of the requested parameters is unknown
- client: raise an exception if the requested pointId is not valid
- data: add helpers to get the closest point/station from given coordinates (#23)
- innosea: add notebook
- innosea: add python code to integrate
- innosea: add test
- innosea: another optimisation
- innosea: cleaning of source code
- innosea: convert input xls file to csv for future test
- innosea: integration
- innosea: interactif notebook
- innosea: optimize wave spectrum creation
- innosea: provide an input so that user can view their selection (#24)
- nataf: provide an input so that user can view their selection (#24)
- spectrum: add a function to compute dispersion (#19)
- spectrum: add a function to convert 2D to 1D spectrum (#19)
- spectrum: add functions to compute sea state parameters from spectrums (#19)
- weather_window: provide an input so that user can view their selection (#24)

### 🚀 Performance improvements

- innosea: build power_t dataframe using matrix operation instead of loops
- innosea: compute wave_power and c_g outside of the loop to use numpy array
- innosea: remove extra lists, data are already available as Series
- innosea: rewrite interp_freq to use sets instead of lists to test inclusion
- innosea: rewrite is_same_freq to use array operation instead of loops
- innosea: use index instead of value to retrieve position
- innosea: use numexpr to boost Jonswap spectrum computation

### 👷 Bug fixes

- check-manifest:  include markdown files
- client: explicitly ask to convert to int64 to get same result on Linux and Windows (#8)

### 📝 Documentation

- add a documentation on how to install the package
- add a sphinx-doc and autogenerate it from docstrings
- add doctest
- improve docstrings / reformat them to be more numpy style
- replace `__token__` by `<username>` which is needed if we build the token ourselve
- spectrum: add auto-documentation about spectrum functions (#19)

### 🤖 Continuous integration

- publish the documentation on pages

### 🤷 Various changes

- add tests for the different method to retreive data
- remove useless data files

## Version 0.2.0 (2021-06-30)
### 🎉 New features

- add static data to the module and provide functions to load them easily (#16)
- add an utility function to set the upper/lower part of a matrix
- nataf: add the censgaussfit function (#10)
- nataf: add the function to compute the gpd parameters
- nataf: add the huseby function (2D and 3D) (#10)
- nataf: add the nataf_simulation function (#10)
- weather_window: migrate the weather windows functions
- notebooks: add a jupyter notebook to make weather window plots
- notebooks: add a jupyter notebook to run the nataf code and make a plot

### 👷 Bug fixes

- data: do not fail loading 'Null' data, and auto complete index when possible (#7)

### 📝 Documentation

- readme: add a step by step installation / configuration / example

### 🤖 Continuous integration

- add mypy
- include templates to drop duplicated pipeline and generate releases on heptapod
- use gitlab-templates to upload the python package to the project's repository

## Version 0.1.0 (2020-09-15)
### New features

- client: fetch data from cassandra and return them as a pandas dataframe
- client: add a _get_raw_data method that fetches the cassandra response to a query
- utils: add a default logger, and logger the get_config function
- utils: add an utility function to get resourcecode configuration

### Documentation

- readme: add a step by step installation / configuration / example

### Various changes

- add a check-manifest test
- Initial commit
