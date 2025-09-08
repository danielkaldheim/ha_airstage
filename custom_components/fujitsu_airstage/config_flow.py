"""Config flow for Airstage Fujitsu integration."""

from __future__ import annotations

import logging
from ipaddress import ip_address
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
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo

from .const import (
    AIRSTAGE_LOCAL_RETRY,
    AIRSTAGE_RETRY,
    CONF_LOCAL,
    CONF_SELECT_POLLING,
    CONF_TURN_ON_BEFORE_SET_TEMP,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

IP_SCHEMA = {
    vol.Required(CONF_IP_ADDRESS): str,
}

LOCAL_DATA_SCHEMA = IP_SCHEMA | {
    vol.Required(CONF_DEVICE_ID): str,
}

CLOUD_DATA_SCHEMA = {
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Optional(CONF_COUNTRY, default="Norway"): str,
}

OPTIONS_SCHEMA = {
    vol.Optional(CONF_TURN_ON_BEFORE_SET_TEMP, default=False): bool,
}


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

        if user_input is not None:
            return self.async_create_entry(
                title=f"{CONF_LOCAL} - {self.config_entry.data[CONF_DEVICE_ID]}",
                data=user_input,
            )

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(OPTIONS_SCHEMA), self.config_entry.options
            ),
            errors=errors,
        )


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Airstage Fujitsu."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlow:
        """Get the Airstage Fujitsu Options flow."""
        return OptionsFlow(config_entry)

    async def async_step_dhcp(
        self,
        discovery_info: DhcpServiceInfo,
    ) -> config_entries.ConfigFlowResult:
        """Handle DHCP discovery flow."""
        _LOGGER.debug("DHCP discovery: %s", discovery_info)
        ip = discovery_info.ip
        mac = discovery_info.macaddress

        for entry in self._async_current_entries():
            if entry.data.get(CONF_DEVICE_ID) == mac.replace(":", "").upper():
                # Device is already configured, check if IP changed
                old_ip = entry.data.get(CONF_IP_ADDRESS)

                if old_ip != ip:
                    _LOGGER.info(
                        "Updating IP for device %s from %s to %s",
                        mac,
                        old_ip,
                        ip,
                    )
                    new_data = {
                        **entry.data,
                        CONF_IP_ADDRESS: ip,
                    }
                    self.hass.config_entries.async_update_entry(
                        entry,
                        data=new_data,
                    )
                return self.async_abort(reason="already_configured")

        # If we get here, the device is not yet configured. Proceed with normal flow
        device_id = mac.replace(":", "").upper()
        user_data = {
            CONF_DEVICE_ID: device_id,
            CONF_IP_ADDRESS: ip,
        }

        # Test to see if we can connect to the device
        try:
            hub = airstage_api.ApiLocal(
                session=async_get_clientsession(self.hass),
                retry=AIRSTAGE_LOCAL_RETRY,
                device_id=user_data[CONF_DEVICE_ID],
                ip_address=user_data[CONF_IP_ADDRESS],
            )
            if not await hub.get_parameters(["iu_model"]):
                return self.async_abort(reason="not_a_fujitsu_airstage")
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            return self.async_abort(reason="not_a_fujitsu_airstage")

        # If successful, create entry
        return self.async_create_entry(
            title=f"Local device {device_id}",
            data=user_data,
        )

    async def async_step_details(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the details step (local or cloud)."""
        errors: dict[str, str] = {}

        if user_input is None:
            return await self.async_step_user()

        data_schema = CLOUD_DATA_SCHEMA  # Default data schema

        # Check if user selected local in a prior step
        if CONF_DEVICE_ID in user_input:
            data_schema = LOCAL_DATA_SCHEMA

        # LOCAL route
        if CONF_DEVICE_ID in user_input or CONF_IP_ADDRESS in user_input:
            try:
                ip_address(user_input[CONF_IP_ADDRESS])
            except ValueError as e:
                errors["base"] = "address/netmask is invalid"
                _LOGGER.warning(errors["base"], exc_info=e)
            except Exception as e:  # noqa: BLE001
                errors["base"] = "address/netmask is invalid"
                _LOGGER.warning(errors["base"], exc_info=e)

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
                        retry=AIRSTAGE_LOCAL_RETRY,
                        device_id=user_input[CONF_DEVICE_ID],
                        ip_address=user_input[CONF_IP_ADDRESS],
                    )

                    if not await hub.get_parameters(["iu_model"]):
                        raise InvalidAuth
                except airstage_api.ApiError as e:
                    errors["base"] = "cannot_connect"
                    _LOGGER.warning(errors["base"], exc_info=e)
                except CannotConnect as e:
                    errors["base"] = "cannot_connect"
                    _LOGGER.warning(errors["base"], exc_info=e)
                except InvalidAuth as e:
                    errors["base"] = "invalid_auth"
                    _LOGGER.warning(errors["base"], exc_info=e)
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
        """Set up a new device."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if CONF_DEVICE_ID in user_input or CONF_IP_ADDRESS in user_input:
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
                    try:
                        # Attempt to connect
                        hub = airstage_api.ApiLocal(
                            session=async_get_clientsession(self.hass),
                            retry=AIRSTAGE_LOCAL_RETRY,
                            device_id=user_input[CONF_DEVICE_ID],
                            ip_address=user_input[CONF_IP_ADDRESS],
                        )

                        if not await hub.get_parameters(["iu_model"]):
                            raise InvalidAuth
                    except airstage_api.ApiError as e:
                        errors["base"] = "cannot_connect"
                        _LOGGER.debug(errors["base"], exc_info=e)
                    except CannotConnect as e:
                        errors["base"] = "cannot_connect"
                        _LOGGER.debug(errors["base"], exc_info=e)
                    except InvalidAuth as e:
                        errors["base"] = "invalid_auth"
                        _LOGGER.debug(errors["base"], exc_info=e)
                    except Exception:  # pylint: disable=broad-except
                        _LOGGER.exception("Unexpected exception")
                        errors["base"] = "unknown"
                    else:
                        data_input = {
                            k: v
                            for k, v in user_input.items()
                            if k != CONF_TURN_ON_BEFORE_SET_TEMP
                        }
                        user_options = {
                            CONF_TURN_ON_BEFORE_SET_TEMP: user_input.get(
                                CONF_TURN_ON_BEFORE_SET_TEMP
                            )
                        }
                        return self.async_create_entry(
                            title=f"{CONF_LOCAL} - {user_input[CONF_DEVICE_ID]}",
                            data=data_input,
                            options=user_options,
                        )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(LOCAL_DATA_SCHEMA | OPTIONS_SCHEMA),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate IP if user changed it
            current_ip = self._get_reconfigure_entry().data[CONF_IP_ADDRESS]
            new_ip = user_input[CONF_IP_ADDRESS]

            try:
                ip_address(new_ip)
            except ValueError as e:
                errors["base"] = "invalid_ip"
                _LOGGER.warning("Error reconfiguring device", exc_info=e)
            else:
                return self.async_update_reload_and_abort(
                    self._get_reconfigure_entry(),
                    data_updates=user_input,
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(IP_SCHEMA), self._get_reconfigure_entry().data
            ),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
