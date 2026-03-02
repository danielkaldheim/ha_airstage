"""The Airstage Fujitsu integration."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp
import pyairstage.airstageApi as airstage_api
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
from homeassistant.exceptions import ConfigEntryNotReady, PlatformNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    AIRSTAGE_LOCAL_RETRY,
    AIRSTAGE_LOCAL_TIMEOUT_SECONDS,
    AIRSTAGE_RETRY,
    AIRSTAGE_SYNC_INTERVAL,
    AIRSTAGE_SYNC_LOCAL_INTERVAL,
    CONF_USE_HTTPS,
    DOMAIN,
)
from .models import AirstageData

_LOGGER = logging.getLogger(__name__)


PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.BINARY_SENSOR,
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
                raise PlatformNotReady(
                    f"Connection error while connecting to Fujitsu Cloud: {err}"
                ) from err

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
        device_id = entry.data[CONF_DEVICE_ID]
        device_ip = entry.data[CONF_IP_ADDRESS]
        use_https = entry.data.get(CONF_USE_HTTPS, False)
        apiLocal = airstage_api.ApiLocal(
            session=async_get_clientsession(hass),
            retry=AIRSTAGE_LOCAL_RETRY,
            timeout_seconds=AIRSTAGE_LOCAL_TIMEOUT_SECONDS,
            device_id=device_id,
            ip_address=device_ip,
            use_https=use_https,
        )

        hass.data.setdefault(
            DOMAIN,
            {
                CONF_DEVICE_ID: device_id,
                CONF_IP_ADDRESS: device_ip,
                CONF_USE_HTTPS: use_https,
            },
        )

        async def async_get():
            try:
                return await apiLocal.get_devices()
            except (
                airstage_api.ApiError,
                asyncio.TimeoutError,
                aiohttp.ServerTimeoutError,
            ) as err:
                raise ConfigEntryNotReady(
                    f"Connection error while connecting to {device_ip}: {err}"
                ) from err

        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=f"Fujitsu Airstage {device_id}",
            update_method=async_get,
            update_interval=timedelta(seconds=AIRSTAGE_SYNC_LOCAL_INTERVAL),
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
