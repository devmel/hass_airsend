"""The AirSend component."""
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import discovery
from homeassistant.components.hassio import (
    get_addons_info,
)
from homeassistant.const import CONF_INTERNAL_URL

DOMAIN = "airsend"
AS_TYPE = ["button", "cover", "sensor", "switch"]

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
            addons_info = get_addons_info(hass)
            for name, options in addons_info.items():
                if "_airsend" in name:
                    ip = options["ip_address"]
                    if ip:
                        internalurl = "http://" + str(ip) + ":33863/"
        except:
            pass
    if internalurl != "" and not internalurl.endswith('/'):
        internalurl += "/"
    config[DOMAIN][CONF_INTERNAL_URL] = internalurl
    for plateform in AS_TYPE:
        discovery.load_platform(hass, plateform, DOMAIN, config[DOMAIN].copy(), config)
    return True
