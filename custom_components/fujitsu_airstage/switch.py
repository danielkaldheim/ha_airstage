"""Switch platform for Airstage integration."""
import logging
from typing import Any

from pyairstage import constants

from homeassistant.components.fujitsu_airstage.pyairstage.pyairstage.constants import (
    ACParameter,
)
from .entity import AirstageAcEntity
from .models import AirstageData
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN as AIRSTAGE_DOMAIN,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AdvantageAir switch platform."""

    instance: AirstageData = hass.data[AIRSTAGE_DOMAIN][config_entry.entry_id]

    entities: list[SwitchEntity] = []
    if devices := instance.coordinator.data:
        for ac_key in devices:
            data = {x["name"]: x for x in devices[ac_key]["parameters"]}
            if data["iu_economy"]["value"] != constants.CAPABILITY_NOT_AVAILABLE:
                entities.append(AirstageEcoSwitch(instance, ac_key))
            if data["iu_powerful"]["value"] != constants.CAPABILITY_NOT_AVAILABLE:
                entities.append(AirstagePowerfulSwitch(instance, ac_key))
            if data["ou_low_noise"]["value"] != constants.CAPABILITY_NOT_AVAILABLE:
                entities.append(AirstageOutdoorLowNoiseSwitch(instance, ac_key))
            if data["iu_fan_ctrl"]["value"] != constants.CAPABILITY_NOT_AVAILABLE:
                entities.append(AirstageEnergySaveFanSwitch(instance, ac_key))
            if data["iu_fan_spd"]["value"] != constants.CAPABILITY_NOT_AVAILABLE:
                entities.append(AirstageQuietFanSwitch(instance, ac_key))

    async_add_entities(entities)


class AirstageEcoSwitch(AirstageAcEntity, SwitchEntity):
    """Representation of Airstage eco mode switch."""

    _attr_icon = "mdi:sprout"
    _attr_name = "Economy mode"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, instance: AirstageData, ac_key: str) -> None:
        """Initialize an Airstage eco mode control."""
        super().__init__(instance, ac_key)
        self._attr_unique_id += "-eco"

    @property
    def is_on(self) -> bool:
        """Return the eco mode status."""
        return self._ac.get_economy_mode() == constants.BooleanDescriptors.ON

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn eco mode on."""
        await self._ac.set_economy_mode(constants.BooleanProperty.ON)
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn eco mode off."""
        await self._ac.set_economy_mode(constants.BooleanProperty.OFF)
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity


class AirstagePowerfulSwitch(AirstageAcEntity, SwitchEntity):
    """Representation of Airstage powerful switch."""

    _attr_name = "Powerful"
    _attr_icon = "mdi:wind-power"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, instance: AirstageData, ac_key: str) -> None:
        """Initialize an Airstage powerful control."""
        super().__init__(instance, ac_key)
        self._attr_unique_id += "-powerful"

    @property
    def is_on(self) -> bool:
        """Return the powerful status."""
        return self._ac.get_powerful_mode() == constants.BooleanDescriptors.ON

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn powerful on."""
        await self._ac.set_powerful_mode(constants.BooleanProperty.ON)
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn powerful off."""
        await self._ac.set_powerful_mode(constants.BooleanProperty.OFF)
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity


class AirstageOutdoorLowNoiseSwitch(AirstageAcEntity, SwitchEntity):
    """Representation of Airstage Outdoor unit low noise switch."""

    _attr_name = "Outdoor unit low noise"
    _attr_icon = "mdi:volume-off"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, instance: AirstageData, ac_key: str) -> None:
        """Initialize an Airstage outdoor unit low noise" control."""
        super().__init__(instance, ac_key)
        self._attr_unique_id += "-low-noise"

    @property
    def is_on(self) -> bool:
        """Return the outdoor unit low noise" status."""
        return self._ac.get_outdoor_low_noise() == constants.BooleanDescriptors.ON

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn outdoor unit low noise" on."""
        await self._ac.set_outdoor_low_noise(constants.BooleanProperty.ON)
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn outdoor unit low noise" off."""
        await self._ac.set_outdoor_low_noise(constants.BooleanProperty.OFF)
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity


class AirstageEnergySaveFanSwitch(AirstageAcEntity, SwitchEntity):
    """Representation of Airstage Energy saving fan switch."""

    _attr_name = "Energy saving fan"
    _attr_icon = "mdi:fan"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, instance: AirstageData, ac_key: str) -> None:
        """Initialize an Airstage energy saving fan control."""
        super().__init__(instance, ac_key)
        self._attr_unique_id += "-energy-save"

    @property
    def is_on(self) -> bool:
        """Return the energy saving fan status."""
        return self._ac.get_energy_save_fan() == constants.BooleanDescriptors.ON

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn energy saving fan on."""
        await self._ac.set_energy_save_fan(constants.BooleanProperty.ON)
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn energy saving fan off."""
        await self._ac.set_energy_save_fan(constants.BooleanProperty.OFF)
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity


class AirstageQuietFanSwitch(AirstageAcEntity, SwitchEntity):
    """Representation of Airstage quiet fan switch."""

    _attr_name = "Quiet fan"
    _attr_icon = "mdi:fan-minus"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, instance: AirstageData, ac_key: str) -> None:
        """Initialize an Airstage quiet fan control."""
        super().__init__(instance, ac_key)
        self._attr_unique_id += "-quiet"

    @property
    def is_on(self) -> bool:
        """Return the quiet fan status."""
        return self._ac.get_fan_speed() == constants.FanSpeedDescriptors.QUIET

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn quiet fan on."""
        await self._ac.set_fan_speed(constants.FanSpeed.QUIET)
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn quiet fan off."""
        await self._ac.set_fan_speed(constants.FanSpeed.AUTO)
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity
