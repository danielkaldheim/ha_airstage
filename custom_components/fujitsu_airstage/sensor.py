"""Sensor platform for Airstage integration."""

from __future__ import annotations

from decimal import Decimal

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify
from pyairstage.constants import CAPABILITY_NOT_AVAILABLE, ACParameter

from .const import DOMAIN as AIRSTAGE_DOMAIN
from .entity import AirstageAcEntity
from .models import AirstageData


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
            data = {x["name"]: x for x in devices[ac_key]["parameters"]}
            if (
                data[ACParameter.INDOOR_TEMPERATURE].get(
                    "value", CAPABILITY_NOT_AVAILABLE
                )
                != CAPABILITY_NOT_AVAILABLE
            ):
                entities.append(
                    AirstageTemp(
                        instance,
                        ac_key,
                        ACParameter.INDOOR_TEMPERATURE,
                        "Indoor",
                    )
                )
            if (
                data[ACParameter.OUTDOOR_TEMPERATURE].get(
                    "value", CAPABILITY_NOT_AVAILABLE
                )
                != CAPABILITY_NOT_AVAILABLE
            ):
                entities.append(
                    AirstageTemp(
                        instance,
                        ac_key,
                        ACParameter.OUTDOOR_TEMPERATURE,
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
        parameter: ACParameter,
        name: str,
    ) -> None:
        """Initialize an Airstage Temp Sensor."""
        super().__init__(instance, ac_key)
        self.parameter = parameter
        self._attr_name = f"{name} temperature"
        self._attr_unique_id += f"{slugify(name)}-temp"

    @property
    def native_value(self) -> Decimal | None:
        """Return the current value of the measured temperature."""
        if self.parameter is ACParameter.INDOOR_TEMPERATURE:
            value = self._ac.get_display_temperature()
            return Decimal(value) if value is not None else None

        if self.parameter is ACParameter.OUTDOOR_TEMPERATURE:
            value = self._ac.get_outdoor_temperature()
            return Decimal(value) if value is not None else None
