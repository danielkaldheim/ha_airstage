"""Config flow for Airstage Fujitsu integration."""

from __future__ import annotations

from ipaddress import ip_address
import logging
from typing import Any

import pyairstage.airstageApi as airstage_api
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_COUNTRY,
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    AIRSTAGE_RETRY,
    CONF_LOCAL,
    CONF_SELECT_POLLING,
    CONF_TURN_ON_BEFORE_SET_TEMP,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class OptionsFlow(config_entries.OptionsFlow):
    """Handle an options flow for Airstage Fujitsu."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        # We read from config_entry.data because that's where we stored IP
        current_ip = self._config_entry.data.get(CONF_IP_ADDRESS, "")
        current_turn_on_before_set_temp = self._config_entry.options.get(
            CONF_TURN_ON_BEFORE_SET_TEMP, False
        )

        if user_input is not None:
            # Validate IP if user changed it
            new_ip = user_input.get(CONF_IP_ADDRESS, current_ip)

            if new_ip:
                try:
                    ip_address(new_ip)
                except ValueError:
                    errors["base"] = "invalid_ip"
                else:
                    # If IP is good, update config_entry.data
                    new_data = {
                        **self._config_entry.data,
                        CONF_IP_ADDRESS: new_ip,
                        CONF_DEVICE_ID: self._config_entry.data.get(CONF_DEVICE_ID, ""),
                    }

                    # Update config_entry.data
                    self.hass.config_entries.async_update_entry(
                        self._config_entry,
                        data=new_data,
                        options={
                            **self._config_entry.options,
                            CONF_TURN_ON_BEFORE_SET_TEMP: user_input.get(
                                CONF_TURN_ON_BEFORE_SET_TEMP,
                                current_turn_on_before_set_temp,
                            ),
                        },
                    )
                    return self.async_create_entry(data={})

            # If new_ip was not provided or invalid, show error
            # But also handle toggles in options
            return self.async_show_form(
                step_id="init",
                data_schema=self._build_schema(
                    current_ip, current_turn_on_before_set_temp
                ),
                errors=errors,
            )

        return self.async_show_form(
            step_id="init",
            data_schema=self._build_schema(current_ip, current_turn_on_before_set_temp),
            errors=errors,
        )

    def _build_schema(self, default_ip: str, default_turn_on_before_set_temp: bool):
        """Build the schema for the OptionsFlow form."""
        return vol.Schema(
            {
                vol.Optional(
                    CONF_IP_ADDRESS,
                    description={"suggested_value": default_ip},
                    default=default_ip,
                ): str,
                vol.Optional(
                    CONF_TURN_ON_BEFORE_SET_TEMP,
                    default=default_turn_on_before_set_temp,
                ): bool,
            }
        )


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
        self.turn_on_before_set_temp = False

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlow:
        """Get the Airstage Fujitsu Options flow."""
        return OptionsFlow(config_entry)

    async def async_step_details(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the details step (local or cloud)."""
        errors: dict[str, str] = {}
        local_data_schema = {
            vol.Required(CONF_DEVICE_ID, default=self.device_id): str,
            vol.Required(CONF_IP_ADDRESS, default=self.ip_address): str,
        }
        cloud_data_schema = {
            vol.Required(CONF_USERNAME, default=self.username): str,
            vol.Required(CONF_PASSWORD, default=self.password): str,
            vol.Optional(CONF_COUNTRY, default="Norway"): str,
        }

        data_schema = cloud_data_schema  # Default data schema

        if user_input is None:
            return await self.async_step_user()

        # Check if user selected local in a prior step
        if (
            CONF_SELECT_POLLING in user_input
            and user_input[CONF_SELECT_POLLING] == CONF_LOCAL
        ):
            data_schema = local_data_schema

        # LOCAL route
        if CONF_DEVICE_ID in user_input or CONF_IP_ADDRESS in user_input:
            data_schema = local_data_schema
            try:
                ip_address(user_input[CONF_IP_ADDRESS])
            except ValueError:
                errors["base"] = "address/netmask is invalid"
            except Exception:  # noqa: BLE001
                errors["base"] = "address/netmask is invalid"

            user_input[CONF_DEVICE_ID] = (
                str(user_input[CONF_DEVICE_ID]).replace(":", "").upper()
            )

            if len(user_input[CONF_DEVICE_ID]) != 12:
                errors["base"] = "invalid device id"

            if not errors:
                # Attempt connection
                try:
                    hub = airstage_api.ApiLocal(
                        session=async_get_clientsession(self.hass),
                        retry=AIRSTAGE_RETRY,
                        device_id=user_input[CONF_DEVICE_ID],
                        ip_address=user_input[CONF_IP_ADDRESS],
                    )

                    if not await hub.get_parameters(["iu_model"]):
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
                    # If successful, create entry
                    return self.async_create_entry(
                        title=f"{CONF_LOCAL} - {user_input[CONF_DEVICE_ID]}",
                        data=user_input,
                    )

        # CLOUD route
        if CONF_USERNAME in user_input or CONF_PASSWORD in user_input:
            if (
                not user_input[CONF_USERNAME]
                or not user_input[CONF_PASSWORD]
                or not user_input[CONF_COUNTRY]
            ):
                errors["base"] = "missing_field"
            else:
                # Attempt cloud connection
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
                    # If successful, create entry
                    return self.async_create_entry(
                        title=f"{DOMAIN} - {user_input[CONF_USERNAME]}",
                        data=user_input,
                    )

        return self.async_show_form(
            step_id="details", data_schema=vol.Schema(data_schema), errors=errors
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
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
                except Exception:
                    errors["base"] = "address/netmask is invalid"

                user_input[CONF_DEVICE_ID] = (
                    str(user_input[CONF_DEVICE_ID]).replace(":", "").upper()
                )

                if len(user_input[CONF_DEVICE_ID]) != 12:
                    errors["base"] = "invalid device id"

                if not errors:
                    # Attempt to connect
                    try:
                        hub = airstage_api.ApiLocal(
                            session=async_get_clientsession(self.hass),
                            retry=AIRSTAGE_RETRY,
                            device_id=user_input[CONF_DEVICE_ID],
                            ip_address=user_input[CONF_IP_ADDRESS],
                        )

                        if not await hub.get_parameters(["iu_model"]):
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


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
