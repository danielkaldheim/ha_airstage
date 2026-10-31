"""Isolated regression tests; Home Assistant and network services are mocked.

Run with: python -m unittest discover -s tests -v
These tests exercise the integration, not a running Home Assistant instance.
"""

import importlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "fujitsu_airstage"
MAC = "aa:bb:cc:dd:ee:ff"  # Deliberately outside the old E8FB1C prefix.
DEVICE_ID = "AABBCCDDEEFF"
DOMAIN = "fujitsu_airstage"


class AbortFlow(Exception):
    """Represent the framework abort exception."""


class ApiError(Exception):
    """Represent a device communication failure."""


class UpdateFailed(Exception):
    """Represent a failed coordinator refresh."""


class ConfigFlow:
    """Mock the framework's public flow contract, including reload scheduling."""

    def __init_subclass__(cls, *, domain):
        cls.handler = domain

    async def async_set_unique_id(self, unique_id):
        self.unique_id = unique_id
        return self.hass.config_entries.async_entry_for_domain_unique_id(
            self.handler, unique_id
        )

    def _async_current_entries(self):
        return self.hass.config_entries.entries

    def _abort_if_unique_id_configured(self, updates=None):
        entry = self.hass.config_entries.async_entry_for_domain_unique_id(
            self.handler, self.unique_id
        )
        if entry is None:
            return
        changed = updates is not None and self.hass.config_entries.async_update_entry(
            entry, data={**entry.data, **updates}
        )
        if entry.state in ("loaded", "setup_retry") and (
            changed or (self.source == "dhcp" and entry.state == "setup_retry")
        ):
            self.hass.config_entries.async_schedule_reload(entry.entry_id)
        raise AbortFlow("already_configured")

    def async_abort(self, *, reason):
        return {"type": "abort", "reason": reason}

    def async_create_entry(self, **kwargs):
        return {"type": "create_entry", "unique_id": self.unique_id, **kwargs}

    def async_show_form(self, **kwargs):
        return {"type": "form", **kwargs}


class Coordinator:
    def __init__(self, hass, logger, **kwargs):
        self.update_method = kwargs["update_method"]

    async def async_config_entry_first_refresh(self):
        self.data = await self.update_method()


def module(name, **attrs):
    result = ModuleType(name)
    result.__dict__.update(attrs)
    return result


def load_integration():
    """Import production modules with external services replaced by mocks."""
    constants = {
        "CONF_COUNTRY": "country",
        "CONF_DEVICE_ID": "device_id",
        "CONF_IP_ADDRESS": "ip_address",
        "CONF_PASSWORD": "password",
        "CONF_USERNAME": "username",
        "Platform": SimpleNamespace(
            CLIMATE="climate", SENSOR="sensor", SWITCH="switch", BINARY_SENSOR="binary"
        ),
    }
    registry = module(
        "homeassistant.helpers.device_registry",
        CONNECTION_NETWORK_MAC="mac",
        format_mac=lambda value: ":".join(
            value.lower()[i : i + 2] for i in range(0, 12, 2)
        ),
        async_get=lambda hass: hass.registry,
    )
    api = module("pyairstage.airstageApi", AirstageApi=object, ApiError=ApiError)
    stubs = {
        "aiohttp": module("aiohttp", ServerTimeoutError=TimeoutError),
        "voluptuous": module(
            "voluptuous",
            Required=lambda key, **kwargs: key,
            Optional=lambda key, **kwargs: key,
            Schema=lambda schema: schema,
        ),
        "pyairstage": module("pyairstage", airstageApi=api),
        "pyairstage.airstageApi": api,
        "homeassistant": module("homeassistant"),
        "homeassistant.config_entries": module(
            "homeassistant.config_entries",
            ConfigEntry=SimpleNamespace,
            ConfigFlow=ConfigFlow,
            OptionsFlow=object,
        ),
        "homeassistant.const": module("homeassistant.const", **constants),
        "homeassistant.core": module(
            "homeassistant.core", HomeAssistant=object, callback=lambda func: func
        ),
        "homeassistant.exceptions": module(
            "homeassistant.exceptions", HomeAssistantError=Exception
        ),
        "homeassistant.helpers": module(
            "homeassistant.helpers", device_registry=registry
        ),
        "homeassistant.helpers.device_registry": registry,
        "homeassistant.helpers.aiohttp_client": module(
            "homeassistant.helpers.aiohttp_client",
            async_get_clientsession=lambda hass: object(),
        ),
        "homeassistant.helpers.update_coordinator": module(
            "homeassistant.helpers.update_coordinator",
            DataUpdateCoordinator=Coordinator,
            UpdateFailed=UpdateFailed,
        ),
        "homeassistant.helpers.service_info": module(
            "homeassistant.helpers.service_info"
        ),
        "homeassistant.helpers.service_info.dhcp": module(
            "homeassistant.helpers.service_info.dhcp", DhcpServiceInfo=SimpleNamespace
        ),
    }
    with patch.dict(sys.modules, stubs):
        spec = importlib.util.spec_from_file_location(
            "airstage_under_test",
            COMPONENT / "__init__.py",
            submodule_search_locations=[str(COMPONENT)],
        )
        integration = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = integration
        spec.loader.exec_module(integration)
        flow_module = importlib.import_module("airstage_under_test.config_flow")
        device_module = importlib.import_module("airstage_under_test.device")
    return integration, flow_module, device_module, api


integration, flows, device, api = load_integration()


class Entries:
    def __init__(self, entries):
        self.entries = entries
        self.reloads = []
        self.async_forward_entry_setups = AsyncMock()

    def async_entry_for_domain_unique_id(self, domain, unique_id):
        return next(
            (entry for entry in self.entries if entry.unique_id == unique_id), None
        )

    def async_update_entry(self, entry, **updates):
        changed = any(getattr(entry, key) != value for key, value in updates.items())
        for key, value in updates.items():
            setattr(entry, key, value)
        return changed

    def async_schedule_reload(self, entry_id):
        self.reloads.append(entry_id)


class LocalIpTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.entry = SimpleNamespace(
            entry_id="existing-entry",
            unique_id=None,
            state="loaded",
            source="user",
            update_listeners=[],
            data={
                "device_id": DEVICE_ID,
                "ip_address": "192.168.1.40",
                "conf_use_https": True,
            },
            options={"conf_turn_on_before_set_temp": True},
        )
        self.hass = SimpleNamespace(
            data={},
            config_entries=Entries([self.entry]),
            registry=SimpleNamespace(async_get_or_create=Mock()),
        )
        self.clients = []

        def create_client(**kwargs):
            client = SimpleNamespace(
                **kwargs,
                get_devices=AsyncMock(return_value={DEVICE_ID: {"model": "test"}}),
                get_parameters=AsyncMock(return_value={"iu_model": "test"}),
            )
            self.clients.append(client)
            return client

        api.ApiLocal = Mock(side_effect=create_client)

    def flow(self, source="dhcp"):
        flow = flows.ConfigFlow()
        flow.hass = self.hass
        flow.source = source
        return flow

    async def discover(self, ip="192.168.1.82", mac=MAC):
        return await self.flow().async_step_dhcp(
            SimpleNamespace(ip=ip, macaddress=mac, hostname="airstage")
        )

    async def test_new_ip_reloads_client_and_preserves_identity_and_settings(self):
        await integration.async_setup_entry(self.hass, self.entry)
        old_client = self.clients[-1]
        with self.assertRaisesRegex(AbortFlow, "already_configured"):
            await self.discover()
        self.assertEqual(self.hass.config_entries.reloads, [self.entry.entry_id])
        await integration.async_setup_entry(self.hass, self.entry)
        self.assertIsNot(old_client, self.clients[-1])
        self.assertEqual(self.clients[-1].ip_address, "192.168.1.82")
        self.assertTrue(self.clients[-1].use_https)
        self.assertEqual(self.entry.data["device_id"], DEVICE_ID)
        self.assertEqual(self.entry.options, {"conf_turn_on_before_set_temp": True})
        self.assertEqual(self.entry.unique_id, MAC)
        self.hass.registry.async_get_or_create.assert_called_with(
            config_entry_id=self.entry.entry_id,
            identifiers={(DOMAIN, DEVICE_ID)},
            connections={("mac", MAC)},
            manufacturer="Fujitsu Airstage",
        )

    async def test_offline_legacy_device_is_registered_before_failed_refresh(self):
        api.ApiLocal.side_effect = lambda **kwargs: SimpleNamespace(
            get_devices=AsyncMock(side_effect=ApiError("offline"))
        )
        with self.assertRaises(UpdateFailed):
            await integration.async_setup_entry(self.hass, self.entry)
        self.assertEqual(self.entry.unique_id, MAC)
        self.hass.registry.async_get_or_create.assert_called_once()
        self.entry.state = "setup_retry"
        with self.assertRaises(AbortFlow):
            await self.discover()
        self.assertEqual(self.entry.data["ip_address"], "192.168.1.82")
        self.assertEqual(self.hass.config_entries.reloads, [self.entry.entry_id])

    async def test_same_ip_does_not_reload_loaded_entry(self):
        with self.assertRaises(AbortFlow):
            await self.discover(ip="192.168.1.40")
        self.assertEqual(self.hass.config_entries.reloads, [])
        api.ApiLocal.assert_not_called()

    async def test_same_ip_retries_an_offline_entry(self):
        self.entry.state = "setup_retry"
        with self.assertRaises(AbortFlow):
            await self.discover(ip="192.168.1.40")
        self.assertEqual(self.hass.config_entries.reloads, [self.entry.entry_id])

    async def test_repeated_discovery_does_not_schedule_another_reload(self):
        for _ in range(2):
            with self.assertRaises(AbortFlow):
                await self.discover()
        self.assertEqual(self.hass.config_entries.reloads, [self.entry.entry_id])

    async def test_dhcp_matches_mac_case_and_separator_variants(self):
        for mac in [MAC.upper(), DEVICE_ID.lower(), "AA-BB-CC-DD-EE-FF"]:
            with self.assertRaises(AbortFlow):
                await self.discover(mac=mac)
        self.assertEqual(self.entry.data["ip_address"], "192.168.1.82")
        self.assertEqual(self.hass.config_entries.reloads, [self.entry.entry_id])

    async def test_unrelated_mac_does_not_change_or_create_entries(self):
        result = await self.discover(mac="11:22:33:44:55:66")
        self.assertEqual(result, {"type": "abort", "reason": "not_configured"})
        self.assertEqual(self.entry.data["ip_address"], "192.168.1.40")
        self.assertIsNone(self.entry.unique_id)
        self.assertEqual(self.hass.config_entries.reloads, [])
        api.ApiLocal.assert_not_called()

    async def test_invalid_mac_is_ignored(self):
        self.assertEqual((await self.discover(mac="not-a-mac"))["type"], "abort")
        self.assertIsNone(self.entry.unique_id)
        self.assertEqual(self.hass.config_entries.reloads, [])

    async def test_manual_setup_rejects_existing_legacy_device_before_connecting(self):
        for step in ["async_step_user", "async_step_details"]:
            with self.assertRaises(AbortFlow):
                await getattr(self.flow("user"), step)(
                    {"device_id": MAC, "ip_address": "192.168.1.82"}
                )
        api.ApiLocal.assert_not_called()
        self.assertEqual(self.entry.data["ip_address"], "192.168.1.40")

    async def test_new_manual_device_gets_normalized_id_and_unique_id(self):
        self.hass.config_entries.entries.clear()
        for step in ["async_step_user", "async_step_details"]:
            result = await getattr(self.flow("user"), step)(
                {
                    "device_id": " aa-bb-cc-dd-ee-ff ",
                    "ip_address": "192.168.1.82",
                    "conf_use_https": True,
                    "conf_turn_on_before_set_temp": True,
                }
            )
            self.assertEqual(result["type"], "create_entry")
            self.assertEqual(result["unique_id"], MAC)
            self.assertEqual(result["data"]["device_id"], DEVICE_ID)

    async def test_existing_unique_id_is_preserved_on_setup(self):
        self.entry.unique_id = MAC
        await integration.async_setup_entry(self.hass, self.entry)
        self.assertEqual(self.entry.unique_id, MAC)

    async def test_setup_does_not_assign_an_existing_unique_id_twice(self):
        other = SimpleNamespace(unique_id=MAC)
        self.hass.config_entries.entries.append(other)
        await integration.async_setup_entry(self.hass, self.entry)
        self.assertIsNone(self.entry.unique_id)

    async def test_cloud_setup_does_not_register_a_local_mac(self):
        self.entry.data = {"username": "test", "password": "test", "country": "Italy"}
        api.ApiCloud = Mock(
            return_value=SimpleNamespace(get_devices=AsyncMock(return_value={}))
        )
        await integration.async_setup_entry(self.hass, self.entry)
        self.assertIsNone(self.entry.unique_id)
        self.hass.registry.async_get_or_create.assert_not_called()
        api.ApiLocal.assert_not_called()


class IdentityTests(unittest.TestCase):
    def test_rejects_non_hexadecimal_device_ids(self):
        self.assertIsNone(device.device_id_to_mac("ZZBBCCDDEEFF"))
        self.assertIsNone(device.device_id_to_mac("AABBCC"))

    def test_manifest_enables_discovery_of_registered_devices(self):
        manifest = json.loads((COMPONENT / "manifest.json").read_text())
        self.assertIn({"registered_devices": True}, manifest["dhcp"])


if __name__ == "__main__":
    unittest.main()
