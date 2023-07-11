"""The Airstage integration models."""
from __future__ import annotations

from dataclasses import dataclass

import pyairstage.api as airstage_api

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


@dataclass
class AirstageData:
    """Data for the Airstage integration."""

    coordinator: DataUpdateCoordinator
    api: airstage_api
