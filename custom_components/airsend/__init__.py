"""The AirSend component."""
import os
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import CONF_INTERNAL_URL

from homeassistant.components.hassio import get_addons_info

DOMAIN = "airsend"
AS_PLATFORMS = ["cover", "switch", "button", "light", "sensor", "binary_sensor"]

_LOGGER = logging.getLogger(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Legacy YAML setup — no longer used for device loading."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AirSend from a config entry."""
    from .coordinator import AirSendCoordinator
    from .device import Device

    hass.data.setdefault(DOMAIN, {})

    internal_url = entry.data.get(CONF_INTERNAL_URL, "")
    devices_config = entry.data.get("devices", {})

    coordinators = {}
    for name, options in devices_config.items():
        device = Device(name, options, internal_url)
        coordinator = AirSendCoordinator(hass, device)
        coordinators[name] = coordinator

    hass.data[DOMAIN][entry.entry_id] = {
        "entry": entry.data,
        "coordinators": coordinators,
    }

    await hass.config_entries.async_forward_entry_setups(entry, AS_PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, AS_PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


def load_airsend_yaml(hass: HomeAssistant) -> dict:
    """Load airsend.yaml resolving !secret tags via secrets.yaml."""
    import yaml as _yaml

    config_dir = hass.config.config_dir
    path = os.path.join(config_dir, "airsend.yaml")

    if not os.path.exists(path):
        _LOGGER.error("airsend.yaml not found at %s", path)
        return {}

    secrets = {}
    secrets_path = os.path.join(config_dir, "secrets.yaml")
    if os.path.exists(secrets_path):
        try:
            with open(secrets_path, "r", encoding="utf-8") as f:
                secrets = _yaml.safe_load(f) or {}
        except Exception as e:
            _LOGGER.warning("Could not load secrets.yaml: %s", e)

    def secret_constructor(loader, node):
        key = loader.construct_scalar(node)
        value = secrets.get(key)
        if value is None:
            _LOGGER.warning("Secret '%s' not found in secrets.yaml", key)
            return ""
        return value

    loader_class = type("SecretLoader", (_yaml.SafeLoader,), {})
    loader_class.add_constructor("!secret", secret_constructor)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = _yaml.load(f, Loader=loader_class)  # noqa: S506
        _LOGGER.debug("airsend.yaml loaded with %d keys", len(data) if data else 0)
        return data or {}
    except Exception as e:
        _LOGGER.error("Failed to load airsend.yaml: %s", e)
        return {}


async def get_internal_url(hass: HomeAssistant) -> str:
    """Auto-detect internal URL of the AirSend addon."""
    try:
        addons_info = get_addons_info(hass)
        for name, options in addons_info.items():
            if "_airsend" in name:
                ip = options.get("ip_address")
                if ip:
                    return "http://" + str(ip) + ":33863/"
    except Exception:
        pass
    return ""
