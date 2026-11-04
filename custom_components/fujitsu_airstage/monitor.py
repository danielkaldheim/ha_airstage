"""Service monitor and function setting values for local Airstage adapters.

The Airstage wireless LAN adapter exposes more than the parameters pyairstage
polls. With the compressor running, ``GetParam`` also answers the "service
monitor" values a technician sees (compressor frequency, coil temperatures,
expansion valve positions, ...). Function settings (the installer settings
11, 30, 31, 42, ... set with the remote controller) are readable as
``iu_fld_set<NN>``.

Observations from a live ASEH14KJCAL on an AOEH30KBTA4 multi split:

* temperatures are reported in 1/100 degC (``2475`` = 24.75 degC);
* ``"65535"`` means the indoor unit does not provide the value;
* ``""`` means no value right now (outdoor values while the compressor is off);
* after a power cycle the adapter has no clock and does not refresh the
  service monitor (intake and coil read a fixed 20.00 degC, outdoor values
  stay empty) until it receives the time with ``SetTime``, as the Airstage
  app does when it connects;
* names the adapter does not know are left out of the response, and a request
  in which *no* name is known fails with error ``0013``.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field

import pyairstage.airstageApi as airstage_api

_LOGGER = logging.getLogger(__name__)

NOT_AVAILABLE = "65535"

# Always-known parameter included in every request, so a request never fails
# with 0013 when none of the extra names is supported.
ANCHOR = "iu_onoff"

MONITOR_PARAMETERS: tuple[str, ...] = (
    "iu_suct_tmp",
    "iu_indoor_tmp_crct",
    "iu_heat_ex_tmp",
    "iu_fan_rot1",
    "ou_cmp_freq",
    "ou_current",
    "ou_four_way_vlv",
    "ou_heat_ex_tmp",
    "ou_heat_ex_tmp_out",
    "ou_fan_rot1",
    "ou_outdoor_tmp",
    "ou_disc_tmp",
    "ou_exp_vlv1",
    "ou_exp_vlv2",
    "ou_exp_vlv3",
    "ou_exp_vlv4",
    "ou_exp_vlv5",
    # Capability flag ("1" = service monitor supported). Lets entities be
    # created even when the adapter has no monitor values yet (just booted).
    "iu_has_srv_mntr",
)

# Monitor names that carry measurements (everything except the flag).
MONITOR_VALUE_NAMES = frozenset(MONITOR_PARAMETERS) - {"iu_has_srv_mntr"}

# Function settings documented for Airstage wall-mounted units (see
# function_settings.py). Must stay below 20 names per request.
FUNCTION_SETTINGS: tuple[int, ...] = (
    0, 11, 30, 31, 35, 36, 40, 42, 43, 44, 46, 48, 49, 60, 95
)

# Run-time counters (unit unconfirmed, probably hours); read with the
# function settings because they change slowly.
COUNTER_PARAMETERS: tuple[str, ...] = (
    "iu_eng_time",
    "iu_cmp_time",
    "iu_fan1_time",
    "ou_fan1_time",
)

# Values the adapter reports before it has read the service monitor.
PLACEHOLDER = {"iu_suct_tmp": "2000", "iu_heat_ex_tmp": "2000", "ou_cmp_freq": ""}

# Minimum time between two SetTime requests sent to wake up the monitor.
SET_TIME_INTERVAL = 600


def is_placeholder(values: dict[str, str]) -> bool:
    """Return True when the monitor values are the adapter's start-up values."""
    return all(values.get(k) == v for k, v in PLACEHOLDER.items())


# Function settings change rarely; read them every N coordinator updates.
# Also the interval for re-checking support that was not detected.
FUNCTION_SETTING_EVERY = 30


def function_setting_name(number: int) -> str:
    """Return the adapter parameter name for a function setting number."""
    return f"iu_fld_set{number}"


def parse_int(raw: str | None) -> int | None:
    """Parse an adapter value, returning None when it is empty or unavailable."""
    if raw is None or raw == "" or raw == NOT_AVAILABLE:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def parse_centi(raw: str | None, signed: bool = True) -> float | None:
    """Parse a value reported in hundredths (temperatures, current)."""
    value = parse_int(raw)
    if value is None:
        return None
    # Assumption: values below zero arrive as 16-bit two's complement.
    if signed and value > 0x7FFF:
        value -= 0x10000
    return round(value / 100, 2)


@dataclass
class MonitorPoller:
    """Fetch extra local parameters and remember what the adapter supports."""

    api: airstage_api.ApiLocal
    monitor_supported: bool | None = None
    functions_supported: bool | None = None
    _cycle: int = 0
    _functions: dict[str, str] = field(default_factory=dict)
    _last_set_time: float | None = None

    async def async_set_time(self) -> None:
        """Send the current time to the adapter (starts its monitor polling)."""
        self._last_set_time = time.monotonic()
        payload = {
            "device_id": self.api.device_id,
            "device_sub_id": 0,
            "req_id": "",
            "modified_by": "",
            "unix_time": int(time.time()),
        }
        try:
            await asyncio.sleep(1)
            response = await self.api.async_call_api(
                "POST",
                f"{self.api.protocol}://{self.api.ip_address}/SetTime",
                json=json.dumps(payload),
            )
        except Exception as err:  # noqa: BLE001 - best effort
            _LOGGER.debug("SetTime failed: %s", err)
        else:
            _LOGGER.debug("SetTime response: %s", response)

    async def _get(self, names: list[str]) -> dict[str, str]:
        # Back-to-back requests make the adapter drop the connection, see
        # pyairstage ApiLocal.get_devices.
        await asyncio.sleep(1)
        values = await self.api.get_parameters([ANCHOR, *names])
        return {k: v for k, v in values.items() if k != ANCHOR}

    async def async_fetch(self) -> dict[str, str]:
        """Return extra parameter values. Never raises."""
        result: dict[str, str] = {}

        # Unsupported is re-checked now and then: right after a power cycle
        # the adapter may not answer the monitor names yet.
        recheck = self._cycle % FUNCTION_SETTING_EVERY == 0
        if self.monitor_supported is not False or recheck:
            try:
                values = await self._get(list(MONITOR_PARAMETERS))
            except Exception as err:  # noqa: BLE001 - optional data, never fatal
                # A timeout is not proof of missing support: retry next cycle.
                _LOGGER.debug("Service monitor values not available: %s", err)
            else:
                if is_placeholder(values):
                    # Adapter lost its clock (power cycle): report nothing
                    # instead of the fixed 20.00 degC and give it the time.
                    values = {
                        k: ("" if k in MONITOR_VALUE_NAMES else v)
                        for k, v in values.items()
                    }
                    if (
                        self._last_set_time is None
                        or time.monotonic() - self._last_set_time
                        >= SET_TIME_INTERVAL
                    ):
                        _LOGGER.info(
                            "Airstage adapter is not reading the service monitor "
                            "(power cycle?), sending the current time"
                        )
                        await self.async_set_time()
                supported = any(v not in ("", NOT_AVAILABLE) for v in values.values())
                if supported or self.monitor_supported is None:
                    self.monitor_supported = supported
                    _LOGGER.debug(
                        "Service monitor supported: %s", self.monitor_supported
                    )
                result.update(values)

        if self.functions_supported is None or recheck:
            try:
                values = await self._get(
                    [function_setting_name(n) for n in FUNCTION_SETTINGS]
                    + list(COUNTER_PARAMETERS)
                )
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug("Function settings not available: %s", err)
            else:
                supported = any(v not in ("", NOT_AVAILABLE) for v in values.values())
                if supported or self.functions_supported is None:
                    self.functions_supported = supported
                    _LOGGER.debug(
                        "Function settings readable: %s", self.functions_supported
                    )
                # Keep the last real value when the adapter answers "" (not
                # fetched from the unit yet).
                for name, value in values.items():
                    if value != "" or name not in self._functions:
                        self._functions[name] = value

        self._cycle += 1
        result.update(self._functions)
        return result


def merge_into_devices(devices: dict, device_id: str, values: dict[str, str]) -> None:
    """Add extra values to the parameter list of a local device."""
    device = devices.get(device_id)
    if not device or not values:
        return
    known = {p["name"] for p in device["parameters"]}
    for name, value in values.items():
        if name not in known:
            device["parameters"].append(
                {"name": name, "value": value, "modifiedAt": ""}
            )
