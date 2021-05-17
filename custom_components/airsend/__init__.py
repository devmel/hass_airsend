"""The AirSend component."""
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import discovery
from homeassistant.const import (
    CONF_DEVICES,
)

DOMAIN = "airsend"
AS_TYPE = ['switch', 'cover']

async def async_setup(hass : HomeAssistant, config : ConfigType):
    """Set up the AirSend component."""
    if DOMAIN not in config:
        return True
    for plateform in AS_TYPE:
        discovery.load_platform(hass, plateform, DOMAIN, config[DOMAIN][CONF_DEVICES].copy(), config)
    return True
