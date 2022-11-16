"""The AirSend component."""
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import discovery
from homeassistant.components.hassio import (
    async_get_addon_info,
)
from homeassistant.const import CONF_INTERNAL_URL

DOMAIN = "airsend"
AS_TYPE = ["switch", "cover", "button"]


async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the AirSend component."""
    if DOMAIN not in config:
        return True
    internalurl = ""
    try:
        internalurl = config[DOMAIN][CONF_INTERNAL_URL]
    except KeyError:
        pass
    if internalurl == "":
        try:
            addon_info: dict = await async_get_addon_info(hass, "local_airsend")
            ip = addon_info["ip_address"]
            if ip:
                internalurl = "http://" + str(ip) + ":33863/"
        except KeyError:
            pass
    config[DOMAIN][CONF_INTERNAL_URL] = internalurl
    for plateform in AS_TYPE:
        discovery.load_platform(hass, plateform, DOMAIN, config[DOMAIN].copy(), config)
    return True
