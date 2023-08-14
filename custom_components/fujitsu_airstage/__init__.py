"""The Airstage Fujitsu integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from .models import AirstageData

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_COUNTRY,
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
    CONF_PASSWORD,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant
import pyairstage.airstageApi as airstage_api
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import AIRSTAGE_RETRY, DOMAIN

_LOGGER = logging.getLogger(__name__)

AIRSTAGE_SYNC_INTERVAL = 120
PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Airstage Fujitsu from a config entry."""

    if CONF_USERNAME in entry.data:
        apiCloud = airstage_api.ApiCloud(
            "eu",
            session=async_get_clientsession(hass),
            retry=AIRSTAGE_RETRY,
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            country=entry.data[CONF_COUNTRY],
        )

        hass.data.setdefault(
            DOMAIN,
            {
                CONF_USERNAME: entry.data[CONF_USERNAME],
                CONF_PASSWORD: entry.data[CONF_PASSWORD],
                CONF_COUNTRY: entry.data[CONF_COUNTRY],
            },
        )

        async def async_get():
            try:
                return await apiCloud.get_devices()
            except airstage_api.ApiError as err:
                raise UpdateFailed(err) from err

        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name="Fujitsu Airstage",
            update_method=async_get,
            update_interval=timedelta(seconds=AIRSTAGE_SYNC_INTERVAL),
        )

        await coordinator.async_config_entry_first_refresh()

        hass.data[DOMAIN][entry.entry_id] = AirstageData(coordinator, apiCloud)

        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    if CONF_DEVICE_ID in entry.data:
        apiLocal = airstage_api.ApiLocal(
            session=async_get_clientsession(hass),
            retry=AIRSTAGE_RETRY,
            device_id=entry.data[CONF_DEVICE_ID],
            ip_address=entry.data[CONF_IP_ADDRESS],
        )

        hass.data.setdefault(
            DOMAIN,
            {
                CONF_DEVICE_ID: entry.data[CONF_DEVICE_ID],
                CONF_IP_ADDRESS: entry.data[CONF_IP_ADDRESS],
            },
        )

        async def async_get():
            try:
                return await apiLocal.get_devices()
            except airstage_api.ApiError as err:
                raise UpdateFailed(err) from err

        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name="Fujitsu Airstage",
            update_method=async_get,
            update_interval=timedelta(seconds=AIRSTAGE_SYNC_INTERVAL),
        )

        await coordinator.async_config_entry_first_refresh()

        hass.data[DOMAIN][entry.entry_id] = AirstageData(coordinator, apiLocal)

        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
