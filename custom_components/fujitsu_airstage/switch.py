"""Switch platform for Airstage integration."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyairstage import constants

from .const import DOMAIN as AIRSTAGE_DOMAIN
from .entity import AirstageAcEntity
from .models import AirstageData

# get_fan_speed() returns a FanSpeedDescriptors value, while set_fan_speed()
# expects a FanSpeed value. Only manual fan speeds are restorable after Quiet.
_RESTORABLE_FAN_SPEEDS = {
    constants.FanSpeedDescriptors.LOW: constants.FanSpeed.LOW,
    constants.FanSpeedDescriptors.MEDIUM: constants.FanSpeed.MEDIUM,
    constants.FanSpeedDescriptors.HIGH: constants.FanSpeed.HIGH,
}


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
            entities.append(AirstagePowerSwitch(instance, ac_key))
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
            if data["iu_wifi_led"]["value"] != constants.CAPABILITY_NOT_AVAILABLE:
                entities.append(AirstageIndoorLedSwitch(instance, ac_key))
            if (
                data["iu_hmn_det_auto_save"]["value"]
                != constants.CAPABILITY_NOT_AVAILABLE
            ):
                entities.append(AirstageHumanDetectionAutoSaveSwitch(instance, ac_key))

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
    def is_on(self) -> bool | None:
        """Return the energy saving fan status."""
        try:
            state = self._ac.get_energy_save_fan()
        except (TypeError, ValueError):
            return None

        if state is None:
            return None

        return state == constants.BooleanDescriptors.ON

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
        # Last manual fan speed before Quiet. RAM-only; falls back to LOW after reload.
        self._previous_fan_speed = None

    @property
    def is_on(self) -> bool | None:
        """Return the quiet fan status."""
        try:
            speed = self._ac.get_fan_speed()
        except (TypeError, ValueError):
            return None

        if speed is None:
            return None

        return speed == constants.FanSpeedDescriptors.QUIET

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn quiet fan on."""
        try:
            current = self._ac.get_fan_speed()
        except (TypeError, ValueError):
            current = None
        self._previous_fan_speed = _RESTORABLE_FAN_SPEEDS.get(current)
        await self._ac.set_fan_speed(constants.FanSpeed.QUIET)
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn quiet fan off, restoring the last known manual fan speed."""
        target = self._previous_fan_speed or constants.FanSpeed.LOW
        await self._ac.set_fan_speed(target)
        self._previous_fan_speed = None
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity


class AirstageIndoorLedSwitch(AirstageAcEntity, SwitchEntity):
    """Representation of Airstage Energy saving fan switch."""

    _attr_name = "Indoor LED"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, instance: AirstageData, ac_key: str) -> None:
        """Initialize an Airstage energy saving fan control."""
        super().__init__(instance, ac_key)
        self._attr_unique_id += "-indoor-led"

    @property
    def is_on(self) -> bool:
        """Return the energy saving fan status."""
        return self._ac.get_indoor_led() == constants.BooleanDescriptors.ON

    @property
    def icon(self) -> str:
        """Return a representative icon of the switch."""
        if self.is_on:
            return "mdi:led-on"
        return "mdi:led-variant-off"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn energy saving fan on."""
        await self._ac.set_indoor_led(constants.BooleanProperty.ON)
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn energy saving fan off."""
        await self._ac.set_indoor_led(constants.BooleanProperty.OFF)
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity


class AirstagePowerSwitch(AirstageAcEntity, SwitchEntity):
    """Representation of Airstage power switch."""

    _attr_name = "Power"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, instance: AirstageData, ac_key: str) -> None:
        """Initialize an Airstage power control."""
        super().__init__(instance, ac_key)
        self._attr_unique_id += "-power"

    @property
    def is_on(self) -> bool | None:
        """Return the power status."""
        try:
            state = self._ac.get_device_on_off_state()
        except (TypeError, ValueError):
            return None

        if state is None:
            return None

        return state == constants.BooleanDescriptors.ON

    @property
    def icon(self) -> str:
        """Return a representative icon of the switch."""
        if self.is_on:
            return "mdi:power"
        return "mdi:power-off"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn power on."""
        await self._ac.turn_on()
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn power off."""
        await self._ac.turn_off()
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity


class AirstageHumanDetectionAutoSaveSwitch(AirstageAcEntity, SwitchEntity):
    """Representation of Airstage Human Detection Auto Save switch."""

    _attr_name = "Human Detection"
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_icon = "mdi:account-eye"

    def __init__(self, instance: AirstageData, ac_key: str) -> None:
        """Initialize Airstage Human Detection Auto Save switch."""
        super().__init__(instance, ac_key)
        self._attr_unique_id += "-human-auto-save"

    @property
    def is_on(self) -> bool:
        """Return the Human Detection Auto Save status."""
        return self._ac.get_hmn_detection_auto_save() == constants.BooleanDescriptors.ON

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn Human Detection Auto Save on."""
        await self._ac.set_hmn_detection_auto_save(constants.BooleanProperty.ON)
        await self.instance.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn Human Detection Auto Save off."""
        await self._ac.set_hmn_detection_auto_save(constants.BooleanProperty.OFF)
        await self.instance.coordinator.async_refresh()
