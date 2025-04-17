"""
Configuration utilities for CAMELS-DE.

This module provides functions for managing persistent configuration,
particularly the path to the CAMELS-DE dataset.
"""

import os
from pathlib import Path
from typing import Optional, Union

from pydantic import Field, AliasChoices, AliasPath
from pydantic_settings import BaseSettings, SettingsConfigDict
import platformdirs

# Get the application config directory using platformdirs
CONFIG_DIR = Path(platformdirs.user_config_dir("camelsde"))
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "config.env"


class Settings(BaseSettings):
    """
    Configuration for CAMELS-DE default path.
    Reads from environment or persistent config file.
    """
    CAMELS_DE_PATH: Optional[Path] = Field(
        default=None,
        validation_alias=AliasChoices('CAMELS_DE_PATH')
    )

    model_config = SettingsConfigDict(
        env_file=str(CONFIG_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )


def get_settings() -> Settings:
    """We call this whenever we need the latest settings."""
    return Settings()


def set_camels_path(p: Union[str, Path]) -> None:
    """
    Persistently set the default dataset path by writing to a config file.
    Overwrites any existing CAMELS_DE_PATH entry.
    
    Parameters
    ----------
    p : str or Path
        Path to the CAMELS-DE dataset folder.
    """
    p = Path(p)
    if not p.exists():
        raise ValueError(f"Provided path '{p}' does not exist.")
    
    # Create or update the config file
    config_content = f"CAMELS_DE_PATH={p.resolve()}\n"
    CONFIG_FILE.write_text(config_content, encoding="utf-8")
    
    # Also set environment variable for current session
    os.environ["CAMELS_DE_PATH"] = str(p.resolve())