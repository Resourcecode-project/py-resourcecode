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
