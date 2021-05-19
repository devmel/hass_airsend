<img align="left" width="80" src="https://raw.githubusercontent.com/devmel/hass_airsend/master/icons/icon.png" alt="App icon">

# AirSend Home Assistant

Component for sending radio commands (433-434Mhz) through the AirSend device.

## Installation

1. Add `airsend:` to your HA configuration (see configuration below).
2. Into the terminal, run `wget -q -O - https://raw.githubusercontent.com/devmel/hass_airsend/master/install | bash -`
 OR copy the `airsend` folder into your [custom_components folder](https://developers.home-assistant.io/docs/creating_integration_file_structure/#where-home-assistant-looks-for-integrations).
3. Restart Home Assistant

## Configuration 

### YAML

To integrate `airsend` into Home Assistant, go to `airsend.cloud -> import/export -> Export YAML` and add the contents of the downloaded file into your HA configuration `configuration.yaml`.

Simple example:

```yaml
# Example configuration.yaml entry
airsend:
  devices:
    light:
      id: 9000
      type: 4098
      apiKey: !secret asKey
    prise somfy:
      id: 9010
      type: 4097
      apiKey: !secret asKey
```

## Preview

<img src="https://raw.githubusercontent.com/devmel/hass_airsend/master/img/screenshot.png" height="200"/>
