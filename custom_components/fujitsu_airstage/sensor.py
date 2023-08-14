"""Sensor platform for Airstage integration."""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

import voluptuous as vol

from pyairstage import constants
from .entity import AirstageAcEntity
from .models import AirstageData
from homeassistant.util import slugify

from .const import (
    DOMAIN as AIRSTAGE_DOMAIN,
)

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Airstage sensor platform."""
    instance: AirstageData = hass.data[AIRSTAGE_DOMAIN][config_entry.entry_id]

    entities: list[SensorEntity] = []
    if devices := instance.coordinator.data:
        for ac_key in devices:
            entities.append(
                AirstageTemp(
                    instance, ac_key, constants.ACParameter.INDOOR_TEMPERATURE, "Indoor"
                )
            )
            entities.append(
                AirstageTemp(
                    instance,
                    ac_key,
                    constants.ACParameter.OUTDOOR_TEMPERATURE,
                    "Outdoor",
                )
            )

    async_add_entities(entities)


class AirstageTemp(AirstageAcEntity, SensorEntity):
    """Representation of Airstage temperature sensor."""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        instance: AirstageData,
        ac_key: str,
        parameter: constants.ACParameter,
        name: str,
    ) -> None:
        """Initialize an Airstage Temp Sensor."""
        super().__init__(instance, ac_key)
        self.parameter = parameter
        self._attr_name = f"{name} temperature"
        self._attr_unique_id += f"{slugify(name)}-temp"

    @property
    def native_value(self) -> Decimal:
        """Return the current value of the measured temperature."""
        # value = self._ac.get_device_parameter(self.parameter)
        if self.parameter is constants.ACParameter.INDOOR_TEMPERATURE:
            value = self._ac.get_display_temperature()
            return Decimal(value)

        if self.parameter is constants.ACParameter.OUTDOOR_TEMPERATURE:
            value = self._ac.get_outdoor_temperature()
            return Decimal(value)
