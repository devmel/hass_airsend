<img align="left" width="80" src="https://raw.githubusercontent.com/devmel/hass_airsend/master/icons/icon.png" alt="App icon">

# AirSend Home Assistant

Component for sending radio commands through the AirSend (RF433) or AirSend duo (RF433 & RF868).

## Installation

1. Into the terminal, run `wget -q -O - https://raw.githubusercontent.com/devmel/hass_airsend/master/install | bash -`
 OR copy the `airsend` folder into your [custom_components folder](https://developers.home-assistant.io/docs/creating_integration_file_structure/#where-home-assistant-looks-for-integrations).
2. To allow a local LAN connection please install and start [hass_airsend-addon](https://github.com/devmel/hass_airsend-addon).
3. Restart Home Assistant
4. Add `airsend:` to your HA configuration (see configuration below).
5. Restart Home Assistant

## Configuration 

### YAML

To integrate `airsend` into Home Assistant, go to `airsend.cloud -> import/export -> Export YAML` and add the contents of the downloaded file into your HA configuration `configuration.yaml`.

#### Local LAN connection
The configuration allows to use the local mode (if [hass_airsend-addon](https://github.com/devmel/hass_airsend-addon) is started) by adding the field `spurl: !secret spurl` in each device. In this mode you must modify the file `secrets.yaml` by adding the local url of the AirSend with its local ipv4 (ex: 192.168.x.x so `spurl: sp://airsend_password@192.168.x.x`), the local ipv6 `fe80::` does not work because of virtualization. You can also remove fields `apiKey`.

## Preview

<img src="https://raw.githubusercontent.com/devmel/hass_airsend/master/img/screenshot.png" height="200"/>
