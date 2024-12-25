from homeassistant.components.dhcp import DHCPMatcher

from .const import DOMAIN

DHCP = [
    DHCPMatcher(
        domain=DOMAIN,
        macaddress="e8fb1c*",
    )
]
