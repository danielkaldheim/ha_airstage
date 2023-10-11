"""Climate platform for Airstage integration."""
from __future__ import annotations

import logging
from typing import Any

from pyairstage import constants
from .entity import AirstageAcEntity
from .models import AirstageData

from homeassistant.components.climate import (
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN as AIRSTAGE_DOMAIN,
    FAN_QUIET,
    VERTICAL_HIGH,
    VERTICAL_HIGHEST,
    VERTICAL_LOW,
    VERTICAL_LOWEST,
    VERTICAL_SWING,
)

HA_STATE_TO_FUJITSU = {
    HVACMode.FAN_ONLY: constants.OperationMode.FAN,
    HVACMode.DRY: constants.OperationMode.DRY,
    HVACMode.COOL: constants.OperationMode.COOL,
    HVACMode.HEAT: constants.OperationMode.HEAT,
    HVACMode.AUTO: constants.OperationMode.AUTO,
}


FUJITSU_TO_HA_STATE = {
    constants.OperationModeDescriptors.FAN: HVACMode.FAN_ONLY,
    constants.OperationModeDescriptors.DRY: HVACMode.DRY,
    constants.OperationModeDescriptors.COOL: HVACMode.COOL,
    constants.OperationModeDescriptors.HEAT: HVACMode.HEAT,
    constants.OperationModeDescriptors.AUTO: HVACMode.AUTO,
    constants.OperationModeDescriptors.OFF: HVACMode.OFF,
    constants.CAPABILITY_NOT_AVAILABLE: None,
}

FUJITSU_FAN_TO_HA = {
    constants.FanSpeedDescriptors.QUIET: FAN_QUIET,
    constants.FanSpeedDescriptors.LOW: FAN_LOW,
    constants.FanSpeedDescriptors.MEDIUM: FAN_MEDIUM,
    constants.FanSpeedDescriptors.HIGH: FAN_HIGH,
    constants.FanSpeedDescriptors.AUTO: FAN_AUTO,
    constants.CAPABILITY_NOT_AVAILABLE: None,
}

HA_FAN_TO_FUJITSU = {
    FAN_QUIET: constants.FanSpeed.QUIET,
    FAN_LOW: constants.FanSpeed.LOW,
    FAN_MEDIUM: constants.FanSpeed.MEDIUM,
    FAN_HIGH: constants.FanSpeed.HIGH,
    FAN_AUTO: constants.FanSpeed.AUTO,
}

HA_SWING_TO_FUJITSU = {
    VERTICAL_HIGHEST: constants.VerticalSwingPosition.HIGHEST,
    VERTICAL_HIGH: constants.VerticalSwingPosition.HIGH,
    VERTICAL_LOW: constants.VerticalSwingPosition.LOW,
    VERTICAL_LOWEST: constants.VerticalSwingPosition.LOWEST,
}

FUJITSU_SWING_TO_HA = {
    constants.VerticalPositionDescriptors.HIGHEST: VERTICAL_HIGHEST,
    constants.VerticalPositionDescriptors.HIGH: VERTICAL_HIGH,
    constants.VerticalPositionDescriptors.LOW: VERTICAL_LOW,
    constants.VerticalPositionDescriptors.LOWEST: VERTICAL_LOWEST,
    constants.CAPABILITY_NOT_AVAILABLE: None,
}

SWING_MODES = [
    VERTICAL_SWING,
    VERTICAL_HIGHEST,
    VERTICAL_HIGH,
    VERTICAL_LOW,
    VERTICAL_LOWEST,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    instance: AirstageData = hass.data[AIRSTAGE_DOMAIN][config_entry.entry_id]

    entities: list[ClimateEntity] = []
    if devices := instance.coordinator.data:
        for ac_key in devices:
            entities.append(AirstageAC(instance, ac_key))

    async_add_entities(entities)


class AirstageAC(AirstageAcEntity, ClimateEntity):
    """Airstage unit."""

    _attr_fan_modes = [FAN_QUIET, FAN_LOW, FAN_MEDIUM, FAN_HIGH]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.5
    _attr_max_temp = 32
    _attr_min_temp = 16
    _attr_name = None

    _attr_fan_modes = [FAN_QUIET, FAN_LOW, FAN_MEDIUM, FAN_HIGH, FAN_AUTO]

    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.COOL,
        HVACMode.HEAT,
        HVACMode.FAN_ONLY,
        HVACMode.DRY,
        HVACMode.AUTO,
    ]

    def __init__(self, instance: AirstageData, ac_key: str) -> None:
        """Initialize an AdvantageAir AC unit."""
        super().__init__(instance, ac_key)

    @property
    def target_temperature(self) -> float | None:
        """Return the current target temperature."""
        if self.hvac_mode == HVACMode.FAN_ONLY:
            return self._ac.get_display_temperature()
        if int(self._ac.get_target_temperature()) >= 6553:
            return self._ac.get_display_temperature()
        return self._ac.get_target_temperature()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""

        await self._ac.set_target_temperature(kwargs.get(ATTR_TEMPERATURE))
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._ac.get_display_temperature()

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return the current HVAC modes."""
        om = self._ac.get_operating_mode()
        if om:
            return FUJITSU_TO_HA_STATE[om]
        return HVACMode.OFF

    @property
    def fan_mode(self) -> str | None:
        """Return the current fan modes."""
        return FUJITSU_FAN_TO_HA[self._ac.get_fan_speed()]

    @property
    def swing_mode(self) -> str | None:
        """Return the swing setting.

        Requires ClimateEntityFeature.SWING_MODE.
        """

        if self._ac.get_vertical_swing() != None:
            if self._ac.get_vertical_swing() == constants.BooleanDescriptors.ON:
                return VERTICAL_SWING

        if self._ac.get_vertical_direction() != None:
            return FUJITSU_SWING_TO_HA[self._ac.get_vertical_direction()]

    @property
    def swing_modes(self) -> list[str] | None:
        """Return swing modes if supported."""
        return SWING_MODES if self.swing_mode is not None else None

    async def async_update(self) -> None:
        """Retrieve latest state."""
        await self.async_update_ac()

    async def async_turn_on(self) -> None:
        """Set the HVAC State to on."""
        await self._ac.turn_on()
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

    async def async_turn_off(self) -> None:
        """Set the HVAC State to off."""
        await self._ac.turn_off()
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set the HVAC Mode and State."""
        if hvac_mode == HVACMode.OFF:
            await self._ac.turn_off()
        else:
            _LOGGER.debug(self._ac.get_device_on_off_state())
            if self._ac.get_device_on_off_state() == constants.BooleanDescriptors.OFF:
                await self._ac.turn_on()
            await self._ac.set_operation_mode(HA_STATE_TO_FUJITSU[hvac_mode])
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set the Fan Mode."""
        await self._ac.set_fan_speed(HA_FAN_TO_FUJITSU[fan_mode])
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        if swing_mode == VERTICAL_SWING:
            await self._ac.set_vertical_swing(constants.BooleanProperty.ON)
        else:
            await self._ac.set_vertical_direction(HA_SWING_TO_FUJITSU[swing_mode])
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Return the list of supported features."""
        supported_features = ClimateEntityFeature.FAN_MODE

        if self.hvac_mode != HVACMode.FAN_ONLY and int(self._ac.get_target_temperature()) < 6553:
            supported_features |= ClimateEntityFeature.TARGET_TEMPERATURE

        if self.swing_mode:
            supported_features |= ClimateEntityFeature.SWING_MODE
        return supported_features
