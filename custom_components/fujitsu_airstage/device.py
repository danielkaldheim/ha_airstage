"""Stable identifiers for local Airstage devices."""

import re

from homeassistant.helpers.device_registry import format_mac


def normalize_device_id(device_id: str) -> str:
    """Return the device ID expected by the local API."""
    return device_id.strip().replace(":", "").replace("-", "").upper()


def device_id_to_mac(device_id: str) -> str | None:
    """Return a registry MAC address, or None for a non-MAC device ID."""
    device_id = normalize_device_id(device_id)
    if not re.fullmatch(r"[0-9A-F]{12}", device_id):
        return None
    return format_mac(device_id)
