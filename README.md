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
> The package requires the CAMELS-DE dataset to be downloaded and extracted. By default, it looks for the data in the `datasets/CAMELS_DE_v1_0_0` directory. You can specify a different path when initializing the `CAMELS_DE` class.
>
> CAMELS-DE can be downloaded from Zenodo: [10.5281/zenodo.13837553](https://doi.org/10.5281/zenodo.13837553)

* The package uses `polars` for reading csv files efficiently, but the functions return `pandas` DataFrames at the moment.
* Gauging station point locations and catchment polygons are returned as `geopandas` GeodataFrames.
* Interactive time series plots are created using `plotly`. 

```python
from camelsde import CAMELS_DE

# Initialize with default path (datasets/CAMELS_DE_v1_0_0)
camelsde = CAMELS_DE()

# Or specify a custom path to the extracted CAMELS-DE directory
# camelsde = CAMELS_DE(path="/path/to/camelsde/data")

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

The dataset needs to be downloaded and extracted before using this package. By default, the package looks for the data in the `datasets/CAMELS_DE_v1_0_0` directory.

## Citation

If you use this package or the CAMELS-DE dataset in your research, please cite both the data description paper and the dataset itself:
- Dataset: [CAMELS-DE v1.0.0](https://doi.org/10.5281/zenodo.13837553)
- Data description paper: [CAMELS-DE: hydrometeorological time series and attributes for 1582 catchments in Germany](https://doi.org/10.5194/essd-16-5625-2024)

## License

This package is distributed under the CC0 1.0 Universal License. See the LICENSE file for more information.
