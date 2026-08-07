"""Climate platform for Airstage integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    PRESET_NONE,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyairstage import constants

from .const import (
    CONF_TURN_ON_BEFORE_SET_TEMP,
)
from .const import DOMAIN as AIRSTAGE_DOMAIN
from .const import (
    FAN_QUIET,
    MINIMUM_HEAT,
    VERTICAL_SWING,
)
from .entity import READ_ERRORS, AirstageAcEntity
from .models import AirstageData

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
    constants.FanSpeedDescriptors.MEDIUM_LOW: "medium-low",
    constants.FanSpeedDescriptors.MEDIUM: FAN_MEDIUM,
    constants.FanSpeedDescriptors.MEDIUM_HIGH: "medium-high",
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


def ha_swing_to_fujitsu(ha_swing: str) -> constants.VerticalSwingPositions:
    return constants.VerticalSwingPositions(ha_swing)


def fujitsu_swing_to_ha(fujitsu_swing: constants.VerticalSwingPositions) -> str:
    return str(fujitsu_swing)


SWING_MODES_4 = [
    VERTICAL_SWING,
    constants.VerticalSwingPositions.HIGHEST,
    constants.VerticalSwingPositions.HIGH,
    constants.VerticalSwingPositions.LOW,
    constants.VerticalSwingPositions.LOWEST,
]

SWING_MODES_6 = [
    VERTICAL_SWING,
    constants.VerticalSwingPositions.HIGHEST,
    constants.VerticalSwingPositions.HIGH,
    constants.VerticalSwingPositions.CENTER_HIGH,
    constants.VerticalSwingPositions.CENTER_LOW,
    constants.VerticalSwingPositions.LOW,
    constants.VerticalSwingPositions.LOWEST,
]

SWING_MODES_8 = [
    VERTICAL_SWING,
    constants.VerticalSwingPositions.HIGHEST,
    constants.VerticalSwingPositions.HIGHER,
    constants.VerticalSwingPositions.HIGH,
    constants.VerticalSwingPositions.CENTER_HIGH,
    constants.VerticalSwingPositions.CENTER_LOW,
    constants.VerticalSwingPositions.LOW,
    constants.VerticalSwingPositions.LOWER,
    constants.VerticalSwingPositions.LOWEST,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    config_entry.async_on_unload(config_entry.add_update_listener(update_listener))

    instance: AirstageData = hass.data[AIRSTAGE_DOMAIN][config_entry.entry_id]

    entities: list[ClimateEntity] = []
    if devices := instance.coordinator.data:
        for ac_key in devices:
            entities.append(AirstageAC(instance, ac_key, config_entry))

    async_add_entities(entities)


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(config_entry.entry_id)


class AirstageAC(AirstageAcEntity, ClimateEntity):
    """Airstage unit."""

    _enable_turn_on_off_backwards_compatibility = False

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.5
    _attr_name = None
    _turn_on_before_set_temp = False

    _attr_fan_modes = [FAN_QUIET, FAN_LOW, FAN_MEDIUM, FAN_HIGH, FAN_AUTO]

    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.COOL,
        HVACMode.HEAT,
        HVACMode.FAN_ONLY,
        HVACMode.DRY,
        HVACMode.AUTO,
    ]

    def __init__(
        self, instance: AirstageData, ac_key: str, config_entry: ConfigEntry
    ) -> None:
        """Initialize an AdvantageAir AC unit."""
        super().__init__(instance, ac_key)
        self._turn_on_before_set_temp = config_entry.options.get(
            CONF_TURN_ON_BEFORE_SET_TEMP, False
        )

    @property
    def target_temperature(self) -> float | None:
        """Return the current target temperature."""
        try:
            target_temp = self._ac.get_target_temperature()
        except READ_ERRORS as e:
            _LOGGER.debug("Could not read target temperature", exc_info=e)
            return self.current_temperature

        if (
            self.hvac_mode == HVACMode.FAN_ONLY
            or target_temp is None
            or int(target_temp) >= 6000
        ):
            return self.current_temperature
        return target_temp

    @property
    def min_temp(self) -> float | None:
        """Return the minimum temperature for the current mode."""
        try:
            value = self._ac.get_minimum_temperature()
        except READ_ERRORS as e:
            _LOGGER.debug("Could not read minimum temperature", exc_info=e)
            value = None

        return value or constants.ACConstants.COOL_MIN_TEMP

    @property
    def max_temp(self) -> float | None:
        """Return the maximum temperature for the current mode."""
        try:
            value = self._ac.get_maximum_temperature()
        except READ_ERRORS as e:
            _LOGGER.debug("Could not read maximum temperature", exc_info=e)
            value = None

        return value or constants.ACConstants.HEAT_MAX_TEMP

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if self._turn_on_before_set_temp and self.hvac_mode == HVACMode.OFF:
            await self.async_turn_on()

        new_hvac_mode = kwargs.get(ATTR_HVAC_MODE)

        if new_hvac_mode is not None and new_hvac_mode != self.hvac_mode:
            # TODO: come up with multi-set option through pyairstage
            await self._ac.set_operation_mode(HA_STATE_TO_FUJITSU[new_hvac_mode])
            await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

        if self.hvac_mode != HVACMode.FAN_ONLY:
            await self._ac.set_target_temperature(kwargs.get(ATTR_TEMPERATURE))
            await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        try:
            return self._ac.get_display_temperature()
        except READ_ERRORS as e:
            _LOGGER.debug("Could not read display temperature", exc_info=e)
            return None

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return the current HVAC modes."""
        try:
            om = self._ac.get_operating_mode()
        except READ_ERRORS as e:
            # Report "unknown" rather than a fabricated OFF: an automation
            # asking "is it off?" must not be told yes because a poll came
            # back partial while the unit is actually running.
            _LOGGER.debug("Could not determine operating mode", exc_info=e)
            return None

        if om:
            return FUJITSU_TO_HA_STATE.get(om, HVACMode.OFF)
        return HVACMode.OFF

    @property
    def fan_mode(self) -> str | None:
        """Return the current fan modes."""
        try:
            fan = self._ac.get_fan_speed()
        except READ_ERRORS as e:
            _LOGGER.debug("Could not determine fan speed", exc_info=e)
            return None

        return FUJITSU_FAN_TO_HA.get(fan) if fan is not None else None

    @property
    def swing_mode(self) -> str | None:
        """Return the swing setting.

        Requires ClimateEntityFeature.SWING_MODE.
        """

        try:
            if self._ac.get_vertical_swing() != None:
                if self._ac.get_vertical_swing() == constants.BooleanDescriptors.ON:
                    return VERTICAL_SWING

            if self._ac.get_vertical_direction() != None:
                return fujitsu_swing_to_ha(self._ac.get_vertical_direction())
        except READ_ERRORS as e:
            # #89 attempting to add some resillience until we can harden
            # pyairstage. Widened from TypeError for #115 / #119: an
            # unsupported total_positions raises AirstageACError, which is not
            # a TypeError, so it escaped here into supported_features and took
            # the whole climate entity down with it.
            _LOGGER.debug("Could not determine swing state", exc_info=e)
            return None

    @property
    def swing_modes(self) -> list[str] | None:
        """Return swing modes if supported."""
        if self.swing_mode:
            try:
                total_positions = self._ac.get_num_vertical_swing_positions()
            except READ_ERRORS as e:
                _LOGGER.debug("Could not read swing positions", exc_info=e)
                return None

            if total_positions == 8:
                return SWING_MODES_8
            elif total_positions == 6:
                return SWING_MODES_6
            elif total_positions == 4:
                return SWING_MODES_4
            else:
                # Was `raise ValueError`. Raising from a property is what
                # removes the entity; a unit that reports a position count we
                # cannot map simply has no swing modes to offer.
                _LOGGER.debug(
                    "Unsupported number of vertical swing positions (%s); "
                    "only 4, 6 and 8 are mapped",
                    total_positions,
                )
                return None
        return None

    @property
    def _minimum_heat(self):
        """Return the minimum-heat state, or None if it cannot be read."""
        try:
            return self._ac.get_minimum_heat()
        except READ_ERRORS as e:
            _LOGGER.debug("Could not determine minimum heat state", exc_info=e)
            return None

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""

        minimum_heat = self._minimum_heat
        if minimum_heat != None:
            if minimum_heat == constants.BooleanDescriptors.ON:
                return MINIMUM_HEAT
            else:
                return PRESET_NONE
        return None

    @property
    def preset_modes(self) -> list[str] | None:
        """Return preset modes if supported."""
        return [PRESET_NONE, MINIMUM_HEAT] if self._minimum_heat is not None else None

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
            await self._ac.set_vertical_direction(ha_swing_to_fujitsu(swing_mode))
        await self.instance.coordinator.async_refresh()  # TODO: see if we can update entity

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        if preset_mode == MINIMUM_HEAT:
            await self._ac.set_minimum_heat(constants.BooleanProperty.ON)
        else:
            await self._ac.set_minimum_heat(constants.BooleanProperty.OFF)
        await self.instance.coordinator.async_refresh()

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Return the list of supported features."""
        supported_features = (
            ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        )

        # Do not vary this by mode, otherwise devices in fan_mode are not referencable in the UX
        supported_features |= ClimateEntityFeature.TARGET_TEMPERATURE

        if self.preset_mode:
            supported_features |= ClimateEntityFeature.PRESET_MODE

        if self.swing_mode:
            supported_features |= ClimateEntityFeature.SWING_MODE
        return supported_features
