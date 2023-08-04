<img align="left" width="80" src="https://raw.githubusercontent.com/devmel/hass_airsend/master/icons/icon.png" alt="App icon">

# AirSend Home Assistant

Component for sending radio commands through the AirSend (RF433) or AirSend duo (RF433 & RF868).

## Installation

1. Install and start [hass_airsend-addon](https://github.com/devmel/hass_airsend-addon).
2. Go to `airsend.cloud -> import/export -> Export YAML` and copy the airsend.yaml file to the folder `config`
2. Add `airsend: !include airsend.yaml` at the end of your `configuration.yaml` file
3. Into the terminal, run `wget -q -O - https://raw.githubusercontent.com/devmel/hass_airsend/master/install | bash -`
 OR copy the `airsend` folder into your [custom_components folder](https://developers.home-assistant.io/docs/creating_integration_file_structure/#where-home-assistant-looks-for-integrations).
4. Restart Home Assistant

## Configuration 

#### Local LAN connection
The configuration allows to use the local mode by adding the field `spurl: !secret spurl` in each device. In this mode you must modify the file `secrets.yaml` by adding the local url of the AirSend with its local ipv4 (ex: 192.168.x.x so `spurl: sp://airsend_password@192.168.x.x`), the local ipv6 `fe80::` does not work because of virtualization. You can also remove fields `apiKey`.
The local mode requires the execution of [hass_airsend-addon](https://github.com/devmel/hass_airsend-addon), if it is not on the same machine it is possible to add the field `internal_url: http://x.x.x.x:33863/` in airsend.conf

## Preview

<img src="https://raw.githubusercontent.com/devmel/hass_airsend/master/img/screenshot.png" height="200"/>
