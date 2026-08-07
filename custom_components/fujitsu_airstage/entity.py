"""Airstage parent entity class."""

import logging
from collections.abc import Callable
from typing import Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pyairstage.airstageAC import AirstageAC, AirstageACError
from pyairstage.airstageApi import ApiError

from .const import DOMAIN
from .models import AirstageData

# Reading a value back out of pyairstage can fail on partial or unexpected
# cached data: AirstageACError for a value the library refuses to interpret
# (e.g. an unsupported total_positions), TypeError/ValueError/KeyError when a
# parameter is absent or does not convert. An entity *property* must never let
# these escape -- see the module docstrings at each call site.
READ_ERRORS = (AirstageACError, TypeError, ValueError, KeyError)

_LOGGER = logging.getLogger(__name__)


class AirstageEntity(CoordinatorEntity):
    """Parent class for Airstage Entities."""

    _attr_has_entity_name = True

    def __init__(self, instance: AirstageData) -> None:
        """Initialize common aspects of an Airstage entity."""
        super().__init__(instance.coordinator)
        # self._attr_unique_id: str = self.coordinator.data["system"]["rid"]

    def update_handle_factory(self, func, *keys):
        """Return the provided API function wrapped.

        Adds an error handler and coordinator refresh, and presets keys.
        """

        async def update_handle(*values):
            try:
                if await func(*keys, *values):
                    await self.coordinator.async_refresh()
            except ApiError as err:
                raise HomeAssistantError(err) from err

        return update_handle


class AirstageAcEntity(AirstageEntity):
    """Parent class for Airstage AC Entities."""

    def __init__(self, instance: AirstageData, ac_key: str) -> None:
        """Initialize common aspects of an Airstage ac entity."""
        super().__init__(instance)
        self.instance = instance

        self.ac_key: str = ac_key
        self._attr_unique_id = f"{ac_key}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            manufacturer="Fujitsu Airstage",
            model=self.coordinator.data[self.ac_key]["model"],
            name=self.coordinator.data[self.ac_key]["deviceName"],
        )

        self.async_update_ac = self.update_handle_factory(instance.api.get_devices)

    @property
    def _ac(self) -> AirstageAC:
        return AirstageAC(self.ac_key, self.instance.api).refresh_parameters(
            data=self.coordinator.data[self.ac_key]
        )

    def read(self, getter: Callable[[AirstageAC], Any], default: Any = None) -> Any:
        """Read a value from pyairstage, degrading to ``default`` on failure.

        ``getter`` receives the ``AirstageAC`` rather than being a bound
        method so that building it happens *inside* the guarded block: a
        device missing from the coordinator's cache raises before any getter
        would run.
        """
        try:
            return getter(self._ac)
        except READ_ERRORS as e:
            _LOGGER.debug(
                "Airstage read failed for %s", self.entity_id or self.ac_key, exc_info=e
            )
            return default

    @property
    def extra_state_attributes(self) -> dict:
        devices = self.instance.coordinator.data
        return {
            str(x["name"]).replace("iu_", ""): x["value"]
            for x in devices[self.ac_key]["parameters"]
        }
