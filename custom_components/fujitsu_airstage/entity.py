"""Airstage parent entity class."""

from typing import Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pyairstage.airstageAC import AirstageAC
from pyairstage.airstageApi import ApiError

from .const import DOMAIN
from .models import AirstageData


def _version_info(device: dict) -> dict[str, str]:
    """Return firmware versions for the device registry (local mode only)."""
    values = {
        p["name"]: p["value"]
        for p in device.get("parameters", [])
        if p.get("value") not in (None, "", "65535")
    }
    info: dict[str, str] = {}
    if main := values.get("iu_main_ver"):
        eeprom = values.get("iu_eep_ver")
        info["sw_version"] = f"{main} (EEPROM {eeprom})" if eeprom else main
    if wla := values.get("wla_main_ver"):
        model = values.get("wla_model")
        info["hw_version"] = f"WLAN adapter {model} {wla}" if model else f"WLAN adapter {wla}"
    return info


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
            **_version_info(self.coordinator.data[self.ac_key]),
        )

        self.async_update_ac = self.update_handle_factory(instance.api.get_devices)

    @property
    def _ac(self) -> AirstageAC:
        return AirstageAC(self.ac_key, self.instance.api).refresh_parameters(
            data=self.coordinator.data[self.ac_key]
        )

    @property
    def extra_state_attributes(self) -> dict:
        devices = self.instance.coordinator.data
        return {
            str(x["name"]).replace("iu_", ""): x["value"]
            for x in devices[self.ac_key]["parameters"]
        }
