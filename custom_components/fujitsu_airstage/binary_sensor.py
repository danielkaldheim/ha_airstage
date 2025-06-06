"""Binary sensor platform for Airstage integration."""

import logging
from typing import Any

from pyairstage import constants

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory

from .entity import AirstageAcEntity
from .models import AirstageData
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
    """Set up Binary sensor platform."""

    instance: AirstageData = hass.data[AIRSTAGE_DOMAIN][config_entry.entry_id]

    entities: list[BinarySensorEntity] = []
    # if devices := instance.coordinator.data:
    #     for ac_key in devices:
    #         data = {x["name"]: x for x in devices[ac_key]["parameters"]}
    #         if data["iu_hmn_det"]["value"] != constants.CAPABILITY_NOT_AVAILABLE:
    #             entities.append(AirstageEcoSwitch(instance, ac_key))

    if entities:
        async_add_entities(entities)


# class AirstageEcoSwitch(AirstageAcEntity, BinarySensorEntity):
#     """Representation of Airstage occupancy sensor."""

#     _attr_name = "Occupancy"
#     _attr_device_class = BinarySensorDeviceClass.OCCUPANCY
#     _attr_entity_category = EntityCategory.DIAGNOSTIC

#     def __init__(self, instance: AirstageData, ac_key: str) -> None:
#         """Initialize an Airstage occupancy sensor."""
#         super().__init__(instance, ac_key)
#         self._attr_unique_id += "-occupancy"

#     @property
#     def is_on(self) -> bool:
#         """Return the occupancy status."""
#         return self._ac.get_human_detection() == constants.BooleanDescriptors.ON
