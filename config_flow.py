"""Config flow for Airstage Fujitsu integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.components.climate import ClimateEntity

from homeassistant.const import CONF_COUNTRY, CONF_USERNAME, CONF_PASSWORD

import pyairstage.api as airstage_api

from .const import AIRSTAGE_RETRY, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Airstage Fujitsu."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.username = None
        self.password = None
        self.country = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if (
                not user_input[CONF_USERNAME]
                or not user_input[CONF_PASSWORD]
                or not user_input[CONF_USERNAME]
            ):
                errors["base"] = "missing_field"
            else:
                try:
                    hub = airstage_api.Api(
                        "eu",
                        session=async_get_clientsession(self.hass),
                        retry=AIRSTAGE_RETRY,
                        username=user_input[CONF_USERNAME],
                        password=user_input[CONF_PASSWORD],
                        country=user_input[CONF_COUNTRY],
                    )

                    if not await hub.authenticate():
                        raise InvalidAuth
                except airstage_api.ApiError:
                    errors["base"] = "cannot_connect"
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except InvalidAuth:
                    errors["base"] = "invalid_auth"
                except Exception:  # pylint: disable=broad-except
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"
                else:
                    return self.async_create_entry(
                        title=f"{DOMAIN} - {user_input['username']}", data=user_input
                    )

        data_schema = {
            vol.Required(CONF_USERNAME, default=self.username): str,
            vol.Required(CONF_PASSWORD, default=self.password): str,
            vol.Optional(
                CONF_COUNTRY,
                default="Norway",
            ): str,
        }

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class AirstageClimate(ClimateEntity):
    """Representation of a Fujitsu Heatpump."""

    def __init__(self, device: dict, hass: HomeAssistant | None) -> None:
        self._hass = hass
        self._airstage_device = device

    @property
    def name(self):
        """Return the name of the climate device."""
        return self._airstage_device["deviceName"]
