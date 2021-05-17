"""AirSend switches."""
import logging
from typing import Any
from requests import get
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.components.cover import (
    CoverEntity,
)
from . import (
    DOMAIN,
)

_LOGGER = logging.getLogger(DOMAIN)

async def async_setup_platform(hass : HomeAssistant, config : ConfigType, async_add_entities, discovery_info=None):
    if discovery_info is None:
        return
    for name, options in discovery_info.items():
        if options['type'] == 4098:
           entity = AirSendCover(hass, name, options['id'], options['type'], options['apiKey'])
           async_add_entities([entity])
    return


class AirSendCover(CoverEntity):
    """Representation of an AirSend Cover."""

    def __init__(self, hass : HomeAssistant, name : str, id: str, type : int, apikey : str):
        """Initialize a cover device."""
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
    def is_closed(self):
        """Return if the cover is closed."""
        return not self._state

    def open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        url = "https://airsend.cloud/device/"+str(self._id)+"/command/5/"
        self._call_cloud(url, True)

    def close_cover(self, **kwargs: Any) -> None:
        """Close cover."""
        url = "https://airsend.cloud/device/"+str(self._id)+"/command/4/"
        self._call_cloud(url, False)

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        url = "https://airsend.cloud/device/"+str(self._id)+"/command/3/"
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
