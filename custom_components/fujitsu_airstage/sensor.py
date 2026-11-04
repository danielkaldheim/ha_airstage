"""Sensor platform for Airstage integration."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfFrequency,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify
from pyairstage import constants

from .const import DOMAIN as AIRSTAGE_DOMAIN
from .entity import AirstageAcEntity
from .models import AirstageData
from .monitor import FUNCTION_SETTINGS, function_setting_name, parse_centi, parse_int


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
            if data["iu_indoor_tmp"]["value"] != constants.CAPABILITY_NOT_AVAILABLE:
                entities.append(
                    AirstageTemp(
                        instance,
                        ac_key,
                        constants.ACParameter.INDOOR_TEMPERATURE,
                        "Indoor",
                    )
                )
            if data["iu_outdoor_tmp"]["value"] != constants.CAPABILITY_NOT_AVAILABLE:
                entities.append(
                    AirstageTemp(
                        instance,
                        ac_key,
                        constants.ACParameter.OUTDOOR_TEMPERATURE,
                        "Outdoor",
                    )
                )

            for description in MONITOR_SENSORS:
                if description.key in data and (
                    data[description.key]["value"] != constants.CAPABILITY_NOT_AVAILABLE
                ):
                    entities.append(
                        AirstageMonitorSensor(instance, ac_key, description)
                    )
            for number in FUNCTION_SETTINGS:
                key = function_setting_name(number)
                if key in data and (
                    data[key]["value"] != constants.CAPABILITY_NOT_AVAILABLE
                ):
                    entities.append(AirstageFunctionSetting(instance, ac_key, number))

    async_add_entities(entities)


@dataclass(frozen=True, kw_only=True)
class AirstageMonitorSensorDescription(SensorEntityDescription):
    """Describes a service monitor sensor."""

    centi: bool = False


MONITOR_SENSORS: tuple[AirstageMonitorSensorDescription, ...] = (
    AirstageMonitorSensorDescription(
        key="iu_suct_tmp",
        name="Intake temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        centi=True,
    ),
    AirstageMonitorSensorDescription(
        key="iu_indoor_tmp_crct",
        name="Corrected intake temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        centi=True,
    ),
    AirstageMonitorSensorDescription(
        key="iu_heat_ex_tmp",
        name="Indoor heat exchanger temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        centi=True,
    ),
    AirstageMonitorSensorDescription(
        key="iu_fan_rot1",
        name="Indoor fan speed",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
    ),
    AirstageMonitorSensorDescription(
        key="ou_cmp_freq",
        name="Compressor frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:engine",
    ),
    AirstageMonitorSensorDescription(
        key="ou_current",
        name="Outdoor unit current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        centi=True,
    ),
    AirstageMonitorSensorDescription(
        key="ou_heat_ex_tmp",
        name="Outdoor heat exchanger temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        centi=True,
    ),
    AirstageMonitorSensorDescription(
        key="ou_outdoor_tmp",
        name="Outdoor unit air temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        centi=True,
    ),
    AirstageMonitorSensorDescription(
        key="ou_disc_tmp",
        name="Compressor discharge temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        centi=True,
    ),
    AirstageMonitorSensorDescription(
        key="ou_four_way_vlv",
        name="4-way valve",
        icon="mdi:valve",
    ),
    *(
        AirstageMonitorSensorDescription(
            key=f"ou_exp_vlv{n}",
            name=f"Expansion valve {n}",
            native_unit_of_measurement="steps",
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:valve",
            entity_registry_enabled_default=n == 1,
        )
        for n in range(1, 6)
    ),
)


class AirstageMonitorSensor(AirstageAcEntity, SensorEntity):
    """Service monitor value reported by the local adapter."""

    entity_description: AirstageMonitorSensorDescription
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        instance: AirstageData,
        ac_key: str,
        description: AirstageMonitorSensorDescription,
    ) -> None:
        """Initialize a service monitor sensor."""
        super().__init__(instance, ac_key)
        self.entity_description = description
        self._attr_unique_id += f"-{description.key}"

    @property
    def native_value(self) -> float | int | None:
        """Return the current value."""
        raw = _raw_value(
            self.coordinator.data, self.ac_key, self.entity_description.key
        )
        if self.entity_description.centi:
            return parse_centi(raw)
        return parse_int(raw)


class AirstageFunctionSetting(AirstageAcEntity, SensorEntity):
    """Function setting (installer setting) read from the indoor unit."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    _attr_icon = "mdi:cog"

    def __init__(self, instance: AirstageData, ac_key: str, number: int) -> None:
        """Initialize a function setting sensor."""
        super().__init__(instance, ac_key)
        self._key = function_setting_name(number)
        self._attr_name = f"Function setting {number:02d}"
        self._attr_unique_id += f"-{self._key}"

    @property
    def native_value(self) -> int | None:
        """Return the setting value."""
        return parse_int(_raw_value(self.coordinator.data, self.ac_key, self._key))


def _raw_value(devices: dict | None, ac_key: str, name: str) -> str | None:
    if not devices or ac_key not in devices:
        return None
    for parameter in devices[ac_key]["parameters"]:
        if parameter["name"] == name:
            return parameter["value"]
    return None


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
    def native_value(self) -> Decimal | None:
        """Return the current value of the measured temperature."""
        # value = self._ac.get_device_parameter(self.parameter)
        if self.parameter is constants.ACParameter.INDOOR_TEMPERATURE:
            value = self._ac.get_display_temperature()
            return Decimal(value) if value is not None else None

        if self.parameter is constants.ACParameter.OUTDOOR_TEMPERATURE:
            value = self._ac.get_outdoor_temperature()
            return Decimal(value) if value is not None else None
