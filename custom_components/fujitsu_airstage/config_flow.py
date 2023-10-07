"""Config flow for Airstage Fujitsu integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from ipaddress import ip_address

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.const import (
    CONF_COUNTRY,
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
    CONF_USERNAME,
    CONF_PASSWORD,
)

from homeassistant.helpers.selector import selector


import pyairstage.airstageApi as airstage_api

from .const import (
    AIRSTAGE_RETRY,
    CONF_CLOUD,
    CONF_LOCAL,
    CONF_SELECT_POLLING,
    CONF_SELECT_POLLING_DESCRIPTION,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Airstage Fujitsu."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.username = None
        self.password = None
        self.country = None
        self.device_id = None
        self.ip_address = None

    async def async_step_details(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        local_data_schema = {
            vol.Required(CONF_DEVICE_ID, default=self.device_id): str,
            vol.Required(CONF_IP_ADDRESS, default=self.ip_address): str,
        }
        cloud_data_schema = {
            vol.Required(CONF_USERNAME, default=self.username): str,
            vol.Required(CONF_PASSWORD, default=self.password): str,
            vol.Optional(
                CONF_COUNTRY,
                default="Norway",
            ): str,
        }

        data_schema = cloud_data_schema  # Default data scheme

        if user_input is None:
            return await self.async_step_user()

        if (
            CONF_SELECT_POLLING in user_input
            and user_input[CONF_SELECT_POLLING] == CONF_LOCAL
        ):
            data_schema = local_data_schema

        if CONF_DEVICE_ID in user_input or CONF_IP_ADDRESS in user_input:
            data_schema = local_data_schema
            try:
                ip_address(user_input[CONF_IP_ADDRESS])
            except ValueError:
                errors["base"] = "address/netmask is invalid"
            except:
                errors["base"] = "address/netmask is invalid"

            user_input[CONF_DEVICE_ID] = (
                str(user_input[CONF_DEVICE_ID]).replace(":", "").upper()
            )

            if len(user_input[CONF_DEVICE_ID]) != 12:
                errors["base"] = "invalid device id"

            if not errors:
                try:
                    hub = airstage_api.ApiLocal(
                        session=async_get_clientsession(self.hass),
                        retry=AIRSTAGE_RETRY,
                        device_id=user_input[CONF_DEVICE_ID],
                        ip_address=user_input[CONF_IP_ADDRESS],
                    )

                    if not await hub.get_parameters(
                        [
                            "iu_model",
                        ],
                    ):
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
                        title=f"{CONF_LOCAL} - {user_input[CONF_DEVICE_ID]}",
                        data=user_input,
                    )

        if CONF_USERNAME in user_input or CONF_PASSWORD in user_input:
            if (
                not user_input[CONF_USERNAME]
                or not user_input[CONF_PASSWORD]
                or not user_input[CONF_COUNTRY]
            ):
                errors["base"] = "missing_field"
            else:
                try:
                    hub = airstage_api.ApiCloud(
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
                        title=f"{DOMAIN} - {user_input[CONF_USERNAME]}",
                        data=user_input,
                    )

        return self.async_show_form(
            step_id="details", data_schema=vol.Schema(data_schema), errors=errors
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the user step."""
        errors: dict[str, str] = {}

        local_data_schema = {
            vol.Required(CONF_DEVICE_ID, default=self.device_id): str,
            vol.Required(CONF_IP_ADDRESS, default=self.ip_address): str,
        }

        data_schema = local_data_schema

        if user_input is not None:
            if CONF_DEVICE_ID in user_input or CONF_IP_ADDRESS in user_input:
                data_schema = local_data_schema
                try:
                    ip_address(user_input[CONF_IP_ADDRESS])
                except ValueError:
                    errors["base"] = "address/netmask is invalid"
                except:
                    errors["base"] = "address/netmask is invalid"

                user_input[CONF_DEVICE_ID] = (
                    str(user_input[CONF_DEVICE_ID]).replace(":", "").upper()
                )

                if len(user_input[CONF_DEVICE_ID]) != 12:
                    errors["base"] = "invalid device id"

                if not errors:
                    try:
                        hub = airstage_api.ApiLocal(
                            session=async_get_clientsession(self.hass),
                            retry=AIRSTAGE_RETRY,
                            device_id=user_input[CONF_DEVICE_ID],
                            ip_address=user_input[CONF_IP_ADDRESS],
                        )

                        if not await hub.get_parameters(
                            [
                                "iu_model",
                            ],
                        ):
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
                            title=f"{CONF_LOCAL} - {user_input[CONF_DEVICE_ID]}",
                            data=user_input,
                        )

        return self.async_show_form(
            step_id="details", data_schema=vol.Schema(data_schema), errors=errors
        )

        # if user_input is not None:
        #     return await self.async_step_details(user_input)

        # return self.async_show_form(
        #     step_id="user",
        #     data_schema=vol.Schema(
        #         {
        #             vol.Required(
        #                 CONF_SELECT_POLLING,
        #                 default=CONF_CLOUD,
        #                 description=CONF_SELECT_POLLING_DESCRIPTION,
        #             ): selector(
        #                 {
        #                     "select": {
        #                         "options": [CONF_LOCAL, CONF_CLOUD],
        #                     }
        #                 }
        #             )
        #         }
        #     ),
        #     errors=errors,
        # )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
