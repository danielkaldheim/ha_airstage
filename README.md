# Fujitsu Airstage Home Assistant component

![Version](https://img.shields.io/github/v/release/danielkaldheim/ha_airstage?style=for-the-badge)
![Contributors](https://img.shields.io/github/contributors/danielkaldheim/ha_airstage?style=for-the-badge)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

Connects your Fujitsu Airstage air conditioner to Home Assistant.

![Example](./docs/Screenshot-device.png)

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/danielkaldheim)


## Installation

### HACS Installation

1. Open HACS
2. Select Integrations, then select the 3-dots in the upper-right corner, then select Custom Repositories.
3. Put the Reposity URL in the Repository field, then select Integration in the Category dropdown list and click Add.
4. Now you can search for Airstage in HACS and install it
5. After the installation you need to restart Home Assistent
6. Now you can skip Configuration and proceed with Usage

### Custom components

1. Download or clone the ha_airstage Integration to your local machine.
2. Navigate to the custom_components directory in your Home Assistant installation directory.
3. Copy the folder custom_components/fujitsu_airstage from the downloaded ha_airstage Integration to the Home Assistant custom_components directory.
5. Restart Home Assistant.

## Configuration

After install go to "Add integration" and search after Fujitsu Airstage.

### Control modes

To add a local device you need the IP Address and Device ID. On my device the MAC address was stated so it was easy to find the IP address on my local network.
The device id is the same as the MAC address exept the ":". Or you can scan the wifi SSID and remove the "AP-WH3X-" the device id is the last 12 characters.

![Local mode](./docs/Screenshot-step2-local.png)

### Local IP address changes

Local devices are registered by their MAC address, independently of their IP
address. When Home Assistant discovers a configured device at a new address, the
integration updates its saved IP and reloads its connection. HTTPS settings,
options, and existing device and entity identifiers are preserved.

Existing local configurations gain a MAC connection and a unique configuration
ID on their next setup. Registration happens before connecting, so a device with
an outdated IP can also recover. Only configured devices are handled by DHCP
discovery; add new devices manually as before.

Home Assistant's DHCP integration must be enabled and able to observe the device
through network discovery or device tracker updates. Recovery is triggered when
Home Assistant learns the new address, not immediately when a router changes its
lease. Networks that hide this information, such as isolated VLANs, may require
manual reconfiguration of the IP address.

To install a local source update:

1. Back up the installed `custom_components/fujitsu_airstage` folder.
2. Copy the complete `custom_components/fujitsu_airstage` folder from this
   repository into Home Assistant's configuration directory, replacing the
   installed files. Include `device.py`, `manifest.json`, and the translations.
3. Restart Home Assistant fully so it reloads the Python code and DHCP manifest.
   Keep the existing integration entries; no removal or re-addition is needed.
4. If the device is already offline, allow network discovery to detect its new
   address. Alternatively, use **Reconfigure** to enter the current IP once.

A later HACS update or reinstall may overwrite local source changes.

### Regression tests

Run `python -m unittest discover -s tests -v`. The tests use mocked Home Assistant
services and network clients; they do not require a running Home Assistant or a
physical air conditioner. Verify DHCP visibility on the target installation too.
