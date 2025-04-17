"""Tests for CAMELS_DE class in the camelsde package."""
import pytest
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from camelsde import CAMELS_DE

# Path to the test data subset
TEST_DATA_PATH = str(Path(__file__).parent / "data" / "camelsde_subset")
# Test gauge IDs to use in tests
TEST_GAUGE_IDS = ["DE110000", "DE110010", "DE110020"]

class TestCAMELSDE:
    """Test cases for the CAMELS_DE class."""
    
    def test_init_with_path(self):
        """Test initializing CAMELS_DE with a specific path."""
        camelsde = CAMELS_DE(path=TEST_DATA_PATH, validate_path=False)
        assert camelsde.path == TEST_DATA_PATH
    
    def test_load_static_attributes(self):
        """Test loading static attributes."""
        camelsde = CAMELS_DE(path=TEST_DATA_PATH, validate_path=False)
        
        # Test loading all attributes
        df = camelsde.load_static_attributes()
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        
        # Test loading specific attribute
        climatic = camelsde.load_static_attributes(static_attribute="climatic")
        assert isinstance(climatic, pd.DataFrame)
        assert not climatic.empty
        assert "p_mean" in climatic.columns
        
        # Test loading with column filter
        cols = ["gauge_id", "p_mean", "area"]
        filtered = camelsde.load_static_attributes(columns=cols)
        assert isinstance(filtered, pd.DataFrame)
        assert filtered.columns.tolist() == cols
    
    def test_load_timeseries(self):
        """Test loading timeseries data."""
        camelsde = CAMELS_DE(path=TEST_DATA_PATH, validate_path=False)
        
        for gauge_id in TEST_GAUGE_IDS:
            # Test loading observed timeseries
            ts = camelsde.load_timeseries(gauge_id=gauge_id)
            assert isinstance(ts, pd.DataFrame)
            assert not ts.empty
            assert "date" in ts.columns
            
            # Test loading simulated timeseries
            sim_ts = camelsde.load_simulated_timeseries(gauge_id=gauge_id)
            assert isinstance(sim_ts, pd.DataFrame)
            assert not sim_ts.empty
            assert "date" in sim_ts.columns
    
    def test_plot_timeseries(self):
        """Test plotting timeseries data."""
        camelsde = CAMELS_DE(path=TEST_DATA_PATH, validate_path=False)
        
        # Test plotting with default options
        fig = camelsde.plot_timeseries(gauge_id=TEST_GAUGE_IDS[0])
        assert isinstance(fig, go.Figure)
        
        # Test plotting with column filtering
        fig = camelsde.plot_timeseries(gauge_id=TEST_GAUGE_IDS[0], columns=["discharge_vol_obs"])
        assert isinstance(fig, go.Figure)
    
    def test_load_geopackage(self):
        """Test loading geopackage data."""
        camelsde = CAMELS_DE(path=TEST_DATA_PATH, validate_path=False)
        
        # Test loading catchments
        catchments = camelsde.load_geopackage(layer="catchments")
        assert not catchments.empty
        
        # Test filtering by gauge IDs
        filtered = camelsde.load_geopackage(layer="catchments", gauge_ids=TEST_GAUGE_IDS)
        assert filtered.shape[0] <= len(TEST_GAUGE_IDS)