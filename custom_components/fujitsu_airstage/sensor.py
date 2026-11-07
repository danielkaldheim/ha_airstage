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
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
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
from .function_settings import FUNCTION_SETTING_INFO, describe_value
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

            # The adapter reports support even before it has values (e.g.
            # just after a power cycle), so create the sensors in that case too.
            has_monitor = (
                data.get("iu_has_srv_mntr", {}).get("value") == "1"
            )
            for description in MONITOR_SENSORS:
                value = data.get(description.key, {}).get("value")
                if (has_monitor and value != constants.CAPABILITY_NOT_AVAILABLE) or (
                    value not in (None, constants.CAPABILITY_NOT_AVAILABLE)
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
    # The adapter answers "" for outdoor values while the compressor is idle;
    # for these sensors that means "not running", so report 0 (debounced).
    zero_when_empty: bool = False


# Consecutive empty answers before compressor/current/fan are reported as 0.
EMPTY_UPDATES_FOR_ZERO = 3

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
        zero_when_empty=True,
    ),
    AirstageMonitorSensorDescription(
        key="ou_current",
        name="Outdoor unit current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        centi=True,
        zero_when_empty=True,
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
        key="ou_heat_ex_tmp_out",
        name="Outdoor heat exchanger outlet temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        centi=True,
    ),
    AirstageMonitorSensorDescription(
        key="ou_fan_rot1",
        name="Outdoor fan speed",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
        zero_when_empty=True,
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
    # Wi-Fi signal of the adapter, read every few minutes with the settings.
    AirstageMonitorSensorDescription(
        key="wla_rssi",
        name="Wi-Fi signal",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    # Run-time counters; unit not confirmed (probably hours), so no unit.
    *(
        AirstageMonitorSensorDescription(
            key=key,
            name=name,
            state_class=SensorStateClass.TOTAL_INCREASING,
            icon="mdi:timer-outline",
            entity_registry_enabled_default=False,
        )
        for key, name in (
            ("iu_eng_time", "Operating time counter"),
            ("iu_cmp_time", "Compressor time counter"),
            ("iu_fan1_time", "Indoor fan time counter"),
            ("ou_fan1_time", "Outdoor fan time counter"),
        )
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
        self._last_value: float | int | None = None
        self._empty_updates = 0
        self._attr_native_value = self._compute_value()

    def _compute_value(self) -> float | int | None:
        raw = _raw_value(
            self.coordinator.data, self.ac_key, self.entity_description.key
        )
        if raw == "" and self.entity_description.zero_when_empty:
            # The adapter also answers "" for a moment while its monitor cache
            # refreshes, so only report 0 when it stays empty.
            self._empty_updates += 1
            if self._empty_updates >= EMPTY_UPDATES_FOR_ZERO:
                self._last_value = 0
            return self._last_value
        self._empty_updates = 0
        value = (
            parse_centi(raw) if self.entity_description.centi else parse_int(raw)
        )
        self._last_value = value
        return value

    def _handle_coordinator_update(self) -> None:
        """Update the value once per coordinator refresh."""
        self._attr_native_value = self._compute_value()
        super()._handle_coordinator_update()


class AirstageFunctionSetting(AirstageAcEntity, SensorEntity):
    """Function setting (installer setting) read from the indoor unit.

    The state shows the code and its meaning ("06 - -2.5 °C ..."); the bare
    code is also available as the ``code`` attribute for automations.
    """

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    _attr_icon = "mdi:cog"

    def __init__(self, instance: AirstageData, ac_key: str, number: int) -> None:
        """Initialize a function setting sensor."""
        super().__init__(instance, ac_key)
        self._number = number
        self._key = function_setting_name(number)
        info = FUNCTION_SETTING_INFO.get(number)
        self._attr_name = f"Function setting {number:02d}" + (
            f" {info.name}" if info else ""
        )
        self._attr_unique_id += f"-{self._key}"

    @property
    def _code(self) -> int | None:
        return parse_int(_raw_value(self.coordinator.data, self.ac_key, self._key))

    @property
    def native_value(self) -> str | None:
        """Return the setting code with its meaning."""
        return describe_value(self._number, self._code)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the bare code and the possible values."""
        attributes: dict[str, Any] = {
            "function_number": self._number,
            "code": self._code,
        }
        if info := FUNCTION_SETTING_INFO.get(self._number):
            attributes["options"] = {
                f"{code:02d}": meaning for code, meaning in info.values.items()
            }
        return attributes


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
