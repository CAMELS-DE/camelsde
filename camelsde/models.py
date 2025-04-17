from typing import List, Optional, Union
import warnings
import os
from pathlib import Path

from pydantic import BaseModel, Field, model_validator
import polars as pl
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go

# Default path for the CAMELS-DE dataset inside this repository
DEFAULT_CAMELS_DE_PATH = str(Path(__file__).parent.parent / "datasets" / "CAMELS_DE_v1_0_0")

class CAMELS_DE(BaseModel):
    """
    Base class for CAMELS DE dataset.

    Attributes
    ----------
    path : str
        Path to the CAMELS-DE dataset folder.  
        Must be CAMELS-DE v1.0.0 at the moment.  
        Defaults to 'datasets/CAMELS_DE_v1_0_0' in the package directory.
    validate_path : bool
        If True, validates the dataset path by checking for the existence of key files.  
        Defaults to True. Can be set to False especially for testing purposes.

    """
    path: str = Field(default=DEFAULT_CAMELS_DE_PATH)
    validate_path: bool = Field(default=True, exclude=True)
    
    @model_validator(mode="before")
    def check_path_validation(cls, values):
        """
        Validate the dataset path based on the validate_path parameter.
        
        This root validator runs before field validation and checks if path validation
        should be performed based on the validate_path parameter.
        """
        path_value = values.get('path', DEFAULT_CAMELS_DE_PATH)
        validate_path = values.get('validate_path', True)
        
        if validate_path:
            path = Path(path_value)
            
            if not path.exists():
                raise ValueError(
                    f"The specified path '{path}' does not exist. "
                    f"Please provide a valid path to the CAMELS-DE dataset or download the dataset "
                    f"from https://zenodo.org/records/13837553 and extract it to {DEFAULT_CAMELS_DE_PATH} "
                    f"or another location specified via the path parameter."
                )
            
            # We check for the number of .csv files that should be present in the dataset
            n_csv_files = len(list(path.rglob("*.csv")))
            if n_csv_files < 3173:
                raise ValueError(
                    f"The specified path '{path}' seems to not contain the complete CAMELS-DE dataset. "
                    f"Please ensure you have downloaded v1.0.0 from https://zenodo.org/records/13837553 "
                    f"and did not modify the folder structure and files."
                    )
        
        # Return the values unchanged
        return values

    def load_static_attributes(self, gauge_id: Optional[str] = None, columns: Optional[List[str]] = None, static_attribute: Optional[str] = None, filters: Optional[dict] = None) -> pd.DataFrame:
        """
        Load static attributes from the dataset with optional filtering and gauge_id selection.  
        Note that the gauge_id column is always included in the returned DataFrame.

        Parameters
        ----------
        gauge_id : str, optional
            The gauge ID for which to load the static attributes. If provided, only the row corresponding to this gauge ID will be returned.
        columns : list of str, optional
            List of column names to load. Can include columns from multiple static attribute files.
        static_attribute : str, optional
            Specify a single static attribute file to load (e.g., "hydrology").
            Valid options are: "climatic", "humaninfluence", "hydrogeology", "hydrology", "landcover", "soil", "topographic".
            If "all" is specified, all static attributes will be loaded.
        filters : dict, optional
            A dictionary where keys are column names and values are lists of tuples of the form (operator, value).
            Supported operators: '==', '!=', '>', '<', '>=', '<='.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the requested static attributes.

        Raises
        ------
        ValueError
            If the static_attribute value is invalid or if requested columns are not found.
        """
        if isinstance(columns, str):
            columns = [columns]

        valid_attributes = {
            "topographic": "CAMELS_DE_topographic_attributes.csv",
            "climatic": "CAMELS_DE_climatic_attributes.csv",
            "humaninfluence": "CAMELS_DE_humaninfluence_attributes.csv",
            "hydrogeology": "CAMELS_DE_hydrogeology_attributes.csv",
            "hydrology": "CAMELS_DE_hydrologic_attributes.csv",
            "landcover": "CAMELS_DE_landcover_attributes.csv",
            "soil": "CAMELS_DE_soil_attributes.csv",
            "simulation_benchmark": "CAMELS_DE_simulation_benchmark.csv",
        }

        if static_attribute and static_attribute not in valid_attributes and static_attribute != "all":
            raise ValueError(
                f"Invalid static_attribute value. Valid options are: {list(valid_attributes.keys()) + ['all']}"
            )

        dfs = []

        if static_attribute == "all" or static_attribute is None:
            files_to_load = valid_attributes.values()
        else:
            files_to_load = [valid_attributes[static_attribute]]

        for file in files_to_load:
            file_path = f"{self.path}/{file}"
            if "topographic" in file:
                # set column provider_id to string
                df = pl.read_csv(file_path, dtypes={"provider_id": str})
            else:
                df = pl.read_csv(file_path)

            dfs.append(df.to_pandas())
            
        df = pd.concat(dfs, axis=1)

        # Make sure that column gauge_id is always present, but only once
        df = df.loc[:, ~df.columns.duplicated()]

        # Filter by gauge_id if provided
        if gauge_id:
            df = df[df["gauge_id"] == gauge_id]
        
        if columns:
            missing_columns = [col for col in columns if col not in df.columns]
            if missing_columns:
                warnings.warn(f"Requested columns not found: {missing_columns}")
                # Remove missing columns from the list
                columns = [col for col in columns if col in df.columns]
            if not columns:
                raise ValueError(f"Columns not found in the static attributes: {columns}")

            # Always keep the gauge_id column at the first position
            if "gauge_id" not in columns:
                columns = ["gauge_id"] + columns

            # Filter the DataFrame to include only the requested columns
            df = df[columns]

        if filters:
            for column, conditions in filters.items():
                if isinstance(conditions, tuple):
                    conditions = [conditions]
                for operator, value in conditions:
                    if operator == "==":
                        df = df[df[column] == value]
                    elif operator == "!=":
                        df = df[df[column] != value]
                    elif operator == ">":
                        df = df[df[column] > value]
                    elif operator == "<":
                        df = df[df[column] < value]
                    elif operator == ">=":
                        df = df[df[column] >= value]
                    elif operator == "<=":
                        df = df[df[column] <= value]
                    else:
                        raise ValueError(f"Unsupported operator: {operator}")

        return df
    
    def load_timeseries(self, gauge_id: str) -> pd.DataFrame:
        """
        Load timeseries data for a specific gauge_id.

        Parameters
        ----------
        gauge_id : str
            The gauge ID for which to load the timeseries data.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the timeseries data for the specified gauge ID.
        """
        file_path = f"{self.path}/timeseries/CAMELS_DE_hydromet_timeseries_{gauge_id}.csv"

        df = pl.read_csv(file_path, try_parse_dates=True)

        return df.to_pandas()
    
    def load_simulated_timeseries(self, gauge_id: str) -> pd.DataFrame:
        """
        Load simulated timeseries data for a specific gauge_id.

        Parameters
        ----------
        gauge_id : str
            The gauge ID for which to load the simulated timeseries data.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the simulated timeseries data for the specified gauge ID.
        """
        file_path = f"{self.path}/timeseries_simulated/CAMELS_DE_discharge_sim_{gauge_id}.csv"
        
        df = pl.read_csv(file_path, try_parse_dates=True)

        # all columns of polars but date and simulation_period are float -> convert
        for col in df.columns:
            if col not in ["date", "simulation_period"]:
                df = df.with_columns(pl.col(col).cast(pl.Float64))

        return df.to_pandas()

    def load_geopackage(self, layer: str, gauge_ids: Optional[List[str]] = None) -> gpd.GeoDataFrame:
        """
        Load geopackage data for catchments or gauging stations.

        Parameters
        ----------
        layer : str
            The layer to load. Must be either 'catchments' or 'gauging_stations'.
        gauge_ids : list of str, optional
            List of gauge IDs to filter the data. If None, all data is loaded.

        Returns
        -------
        gpd.GeoDataFrame
            GeoDataFrame containing the requested geopackage data.
        """
        if layer == "catchments":
            file_path = f"{self.path}/CAMELS_DE_catchment_boundaries/catchments/CAMELS_DE_catchments.gpkg"
        elif layer == "gauging_stations":
            file_path = f"{self.path}/CAMELS_DE_catchment_boundaries/gauging_stations/CAMELS_DE_gauging_stations.gpkg"
        else:
            raise ValueError("Invalid layer. Must be 'catchments' or 'gauging_stations'.")

        gdf = gpd.read_file(file_path)
        if gauge_ids:
            gdf = gdf[gdf["gauge_id"].isin(gauge_ids)]

        return gdf

    def plot_timeseries(self, gauge_id: str, columns: Optional[List[str]] = None) -> go.Figure:
        """
        Plot the timeseries data for a specific gauge_id using Plotly.
        Loads both observed and simulated timeseries data.

        Parameters
        ----------
        gauge_id : str
            The gauge ID for which to plot the timeseries data.
        columns : list of str, optional
            Specific columns to plot. If None, all columns will be plotted.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly figure object for the timeseries plot.
        """
        fig = go.Figure()
        
        # Load both observed and simulated datasets
        observed_df = self.load_timeseries(gauge_id)
        simulated_df = self.load_simulated_timeseries(gauge_id)
        
        # Combine: start with a copy of the observed dataframe
        merged_df = observed_df.copy()
        
        # Add non-overlapping columns from simulated data
        for col in simulated_df.columns:
            if col not in observed_df.columns and col != 'date':
                merged_df[col] = simulated_df[col]
        
        # Filter columns if specified
        if columns:
            available_columns = [col for col in columns if col in merged_df.columns]
            
            if not available_columns:
                warnings.warn(f"No requested columns found in the timeseries data")
                return fig
            
            # Keep only the date column and the requested columns
            plot_df = merged_df[["date"] + available_columns]
        else:
            # Use all columns
            plot_df = merged_df
        
        # Add traces for each column
        for column in plot_df.columns:
            if column != "date":
                fig.add_trace(go.Scatter(
                    x=plot_df["date"], 
                    y=plot_df[column], 
                    mode="lines", 
                    name=column,
                    line=dict(width=2)
                ))

        fig.update_layout(
            title=f"Timeseries for Gauge ID {gauge_id}",
            xaxis_title="Date",
            yaxis_title="Value",
            template="plotly_white"
        )

        return fig
