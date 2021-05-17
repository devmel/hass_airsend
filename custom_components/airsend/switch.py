"""AirSend switches."""
import logging
from typing import Any
from requests import get
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.components.switch import (
    SwitchEntity,
)
from . import (
    DOMAIN,
)

_LOGGER = logging.getLogger(DOMAIN)

async def async_setup_platform(hass : HomeAssistant, config : ConfigType, async_add_entities, discovery_info=None):
    if discovery_info is None:
        return
    for name, options in discovery_info.items():
        if options['type'] == 4096 or options['type'] == 4097:
           entity = AirSendSwitch(hass, name, options['id'], options['type'], options['apiKey'])
           async_add_entities([entity])
    return


class AirSendSwitch(SwitchEntity):
    """Representation of an AirSend Switch."""

    def __init__(self, hass : HomeAssistant, name : str, id: str, type : int, apikey : str):
        """Initialize a switch or light device."""
        self._name = name
        self._id = id
        self._type = type
        self._apikey = apikey
        uname = DOMAIN+name
        self._unique_id = "_".join(x for x in uname)
        self._state = False

    @property
    def unique_id(self):
        """Return unique identifier of remote device."""
        return self._unique_id

    @property
    def available(self):
        return True

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        return None

    @property
    def assumed_state(self):
        """Return true if unable to access real state of entity."""
        return True

    @property
    def is_on(self):
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        command = "1" if self._type == 4097 else "6"
        url = "https://airsend.cloud/device/"+str(self._id)+"/command/"+command+"/"
        self._call_cloud(url, True)

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        command = "0" if self._type == 4097 else "6"
        url = "https://airsend.cloud/device/"+str(self._id)+"/command/"+command+"/"
        self._call_cloud(url, False)

    def _call_cloud(self, url : str, new_state : bool):
        headers = {"Authorization": "Bearer "+self._apikey, "content-type": "application/json", "User-Agent": "hass_airsend"}
        status_code = 404
        try:
            response = get(url, headers=headers)
            status_code = response.status_code
        except:
            pass
        if status_code == 200:
            self._state = new_state
            self.schedule_update_ha_state()
        else:
            _LOGGER.error("airsend.cloud error : "+str(status_code))
            raise Exception("airsend.cloud error : "+str(status_code)) 
