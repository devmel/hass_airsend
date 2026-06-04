[![airsend](https://img.shields.io/github/release/devmel/hass_airsend/all.svg?style=plastic&label=Current%20release)](https://github.com/devmel/hass_airsend) [![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=plastic)](https://github.com/hacs/integration) [![downloads](https://img.shields.io/github/downloads/devmel/hass_airsend/total?style=plastic&label=Total%20downloads)](https://github.com/devmel/hass_airsend)

# AirSend
This is a Home Assistant integration for AirSend boxes, which can capture and control more than 350 equipements (Remote Switchs, Lights, Shutters, Gate... ) from 50 brands (Dio, Faac, Nice, Somfy...) by RF433 or RF868 radio commands.

### Supported boxes
- [AirSend](https://devmel.com/fr/airsend.html) (RF433)
- [AirSend Duo](https://devmel.com/fr/airsend-duo.html) (RF433 & RF868)


Each AirSend device is represented as a proper **Home Assistant device** with its associated entities (cover, switch, button, light, sensor).


## Requirements

### 1. Install the AirSend addon

[![Add AirSend addon repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fdevmel%2Fhass_airsend-addon)

Install and start the **AirSend** addon.

### 2. Create `airsend.yaml`

Export your devices from [airsend.cloud](https://airsend.cloud) → Import/Export → Export YAML (select `spurl` for local connection).

Place the exported `airsend.yaml` in your `/config` folder.

Add your AirSend local connection string to `secrets.yaml`:

```yaml
spurl: sp://**************@[fe80::xxxx:xxxx:xxxx:xxxx]?gw=0&rhost=192.168.xxx.xxx
```

Example `airsend.yaml`:

```yaml
devices:
  AirSend box:
    type: 0
    spurl: !secret spurl
    sensors: true      # enables temperature and illuminance sensors
    bind: 1
    refresh: 300

  Volet salon:
    id: 12345
    type: 4098
    apiKey: !secret apiKey
    spurl: !secret spurl
    channel:
      id: 25455
      source: 94311

  Lumiere pergola:
    id: 65838
    type: 4100         # dimmable light
    apiKey: !secret apiKey
    spurl: !secret spurl
    wait: true
    channel:
      id: 26848
      source: 1442421508
```

## Installation

### Manual installation (until the repository is available in HACS)

1. Download the latest release from [GitHub releases](https://github.com/devmel/hass_airsend/releases).
2. Copy the `custom_components/airsend` directory into your `custom_components` folder.
3. Restart Home Assistant.
4. Go to **Settings → Integrations → Add integration** and search for `AirSend`.

### HACS (recommended)

1. Ensure [HACS](https://hacs.xyz) is installed.
2. Search for `AirSend` in HACS and install it, or use the button below.
3. Restart Home Assistant.
4. Go to **Settings → Integrations → Add integration** and search for `AirSend`.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Devmel&repository=hass_airsend)



## Configuration

After the integration added, the internal URL of the addon will be auto-detected. Confirm and your devices will appear automatically.

To reload devices after modifying `airsend.yaml`, use the **Reconfigure** option on the integration.

## Device options reference

| Option | Description |
|--------|-------------|
| `type` | Device type (see table above) |
| `id` | AirSend cloud device ID |
| `apiKey` | AirSend cloud API key |
| `spurl` | Local connection string |
| `channel` | RF channel definition (`id`, `source`, `mac`, `seed`) |
| `wait` | Wait for RF confirmation before returning (`true`/`false`) |
| `sensors` | Enable temperature and illuminance sensors for AirSend box (`true`/`false`) |
| `bind` | Channel ID to bind for incoming RF messages |
| `refresh` | Poll interval in seconds (default: 300) |

## Informations

This integration requires the [AirSend addon](https://github.com/devmel/hass_airsend-addon) to communicate with your AirSend hardware locally.
For local connection, the AirSend IPv4 address is required, you can find it in your router or [Airsend App for Windows](https://apps.microsoft.com/detail/9nblggh40m8w).
If you `DO NOT` provide ?gw=0&rhost=... then you may face unexpected `HTTP/500` status code or `HTTP/262` status code at Home Assistant level.

## Supported device types

| Type | Value | Description |
|------|-------|-------------|
| AirSend box | `0` | The AirSend hardware box (state, temperature, illuminance) |
| Sensor | `1` | Generic RF sensor |
| Cover | `4098` | Roller shutter, blind (open/close/stop) |
| Cover with position | `4099` | Roller shutter with position control (0-100%) |
| Switch | `4097` | On/Off switch |
| Button | `4096` | Single-action button (toggle) |
| Light | `4100` | Dimmable light (0-100%) |

## Preview

![Screenshot](https://raw.githubusercontent.com/devmel/hass_airsend/master/img/screenshot.png)
