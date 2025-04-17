# CAMELS-DE 🌊

A Python package for working with the [CAMELS-DE dataset](https://doi.org/10.5281/zenodo.13837553).

## About 🐪

CAMELS-DE provides access to hydrometeorological time series data and catchment attributes for 1582 catchments in Germany. This package offers a simple interface for loading, analyzing, and visualizing data from the CAMELS-DE dataset.  

## Installation

```bash
pip install camelsde
```

## Usage

> [!IMPORTANT]
> The package requires the CAMELS-DE dataset to be downloaded and extracted. 
>
> CAMELS-DE can be downloaded from Zenodo: [10.5281/zenodo.13837553](https://doi.org/10.5281/zenodo.13837553)

* The package uses `polars` for reading csv files efficiently, but the functions return `pandas` DataFrames at the moment.
* Gauging station point locations and catchment polygons are returned as `geopandas` GeodataFrames.
* Interactive time series plots are created using `plotly`. 

### Setting the CAMELS-DE Dataset Path

The package will look for the dataset in the following order:

1. `path` argument passed to the `CAMELS_DE` class constructor.
2. User-configured permanent path (if set).
3. `CAMELSDE_PATH` environment variable (if set)

You can set a permanent path to your CAMELS-DE dataset in following ways:

```python
from camelsde import CAMELS_DE, set_camels_path

# Option 1: Temporarily override the path for a specific instance
camelsde = CAMELS_DE(path="/path/to/your/CAMELS_DE_v1_0_0")

# Option 2: Set a permanent path that will be remembered across sessions
set_camels_path("/path/to/your/CAMELS_DE_v1_0_0")

camelsde = CAMELS_DE()  # Now this will use the permanent path

```

The permanent path is stored in a configuration file in your user config directory, which makes it available across all future Python sessions.

### Basic Usage Examples

```python
from camelsde import CAMELS_DE

# Initialize (uses the configured path or default)
camelsde = CAMELS_DE()

# Load static attributes
attributes = camelsde.load_static_attributes()

# Load specific attributes
hydro_attrs = camelsde.load_static_attributes(static_attribute="hydrology")

# Load specific columns across all static attribute files
attributes2 = camelsde.load_static_attributes(columns=["gauge_name", "gauge_elev", "area", "NSE_lstm", "NSE_hbv"])

# Load specific columns and apply filtering
attributes3 = camelsde.load_static_attributes(columns=["gauge_name", "gauge_elev", "area", "NSE_lstm", "NSE_hbv"], filters={"NSE_lstm": (">=", 0.9), "area": [ (">=", 50), ("<=", 100)]})

# Load specific gauge ID
gauge_data = camelsde.load_static_attributes(gauge_id="DE110000")

# Load timeseries data
ts_data = camelsde.load_timeseries(gauge_id="DE110000")

# Plot timeseries with Plotly
camelsde.plot_timeseries(gauge_id="DE110000", columns=["precipitation", "discharge_spec_obs", "discharge_spec_sim_lstm"])

# Load geospatial data (returns a geopandas GeoDataFrame)
catchments = camelsde.load_geopackage(layer="catchments")
stations = camelsde.load_geopackage(layer="gauging_stations")
```

## Dataset

This package works with the CAMELS-DE v1.0.0 dataset, which is publicly available at:
- [CAMELS-DE Dataset on Zenodo](https://doi.org/10.5281/zenodo.13837553)

The dataset needs to be downloaded and extracted before using this package.

## Citation

If you use this package or the CAMELS-DE dataset in your research, please cite both the data description paper and the dataset itself:
- Dataset: [CAMELS-DE v1.0.0](https://doi.org/10.5281/zenodo.13837553)
- Data description paper: [CAMELS-DE: hydrometeorological time series and attributes for 1582 catchments in Germany](https://doi.org/10.5194/essd-16-5625-2024)

## License

This package is distributed under the CC0 1.0 Universal License. See the LICENSE file for more information.
