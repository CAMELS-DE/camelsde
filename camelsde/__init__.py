"""
CAMELS-DE - A Python package for working with the CAMELS-DE dataset.

This package provides tools for accessing, analyzing, and visualizing hydrological data
from the CAMELS-DE (Catchment Attributes and Meteorology for Large-sample Studies - Germany) dataset.
"""

from camelsde.models import CAMELS_DE
from camelsde.config import get_settings, set_camels_path

__version__ = "0.2.0"
__all__ = ["CAMELS_DE"]