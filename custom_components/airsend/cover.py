"""AirSend switches."""
import logging
import json
from typing import Any
from requests import get, post
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.components.hassio import (
    async_get_addon_discovery_info,
    async_get_addon_info,
)
from homeassistant.components.cover import (
    CoverEntity,
)
from . import (
    DOMAIN,
)

_LOGGER = logging.getLogger(DOMAIN)

async def async_setup_platform(hass : HomeAssistant, config : ConfigType, async_add_entities, discovery_info=None):
    addons_url = ""
    try:
        addon_info: dict = await async_get_addon_info(hass, 'local_airsend')
        ip = addon_info["ip_address"]
        if ip:
            addons_url = "http://"+str(ip)+":33863/"
        # _LOGGER.warning("Addon '%s'", addon_info)
    except:
        pass
    if discovery_info is None:
        return
    for name, options in discovery_info.items():
        if options['type'] == 4098:
            id = ""
            apiKey = ""
            spurl = ""
            channel = {}
            try:
                id = options['id']
            except KeyError:
                pass
            try:
                apiKey = options['apiKey']
            except KeyError:
                pass
            try:
                spurl = options['spurl']
            except KeyError:
                pass
            try:
                channel = options['channel']
            except KeyError:
                pass
            entity = AirSendCover(hass, name, id, options['type'], apiKey, addons_url, spurl, channel)
            async_add_entities([entity])
    return


class AirSendCover(CoverEntity):
    """Representation of an AirSend Cover."""

    def __init__(self, hass : HomeAssistant, name : str, id: str, type : int, apikey : str, addons_url : str, spurl : str, channel : dict):
        """Initialize a cover device."""
        self._name = name
        self._id = id
        self._type = type
        self._apikey = apikey
        self._addons_url = addons_url
        self._spurl = spurl
        self._channel = channel
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
        note = {"method":1,"type":0,"value": "UP"}
        url = "https://airsend.cloud/device/"+str(self._id)+"/command/5/"
        payload = '{"wait": true, "channel":'+json.dumps(self._channel)+', "thingnotes":{"notes":['+json.dumps(note)+']}}'
        self._action(url, payload, False)

    def close_cover(self, **kwargs: Any) -> None:
        """Close cover."""
        note = {"method":1,"type":0,"value": "DOWN"}
        url = "https://airsend.cloud/device/"+str(self._id)+"/command/4/"
        payload = '{"wait": true, "channel":'+json.dumps(self._channel)+', "thingnotes":{"notes":['+json.dumps(note)+']}}'
        self._action(url, payload, False)

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        note = {"method":1,"type":0,"value": "STOP"}
        url = "https://airsend.cloud/device/"+str(self._id)+"/command/3/"
        payload = '{"wait": true, "channel":'+json.dumps(self._channel)+', "thingnotes":{"notes":['+json.dumps(note)+']}}'
        self._action(url, payload, False)

    def _action(self, cloud_url : str, payload : str, new_state : bool):
        status_code = 404
        if self._addons_url and self._spurl:
            headers = {"Authorization": "Bearer "+self._spurl, "content-type": "application/json", "User-Agent": "hass_airsend"}
            try:
                response = post(self._addons_url+"airsend/transfer", headers=headers, data=payload, timeout=6)
                status_code = 500
                jdata = json.loads(response.text)
                if jdata["type"] < 0x100:
                    status_code = response.status_code
            except:
                pass
        if status_code != 200 and self._apikey and cloud_url:
            headers = {"Authorization": "Bearer "+self._apikey, "content-type": "application/json", "User-Agent": "hass_airsend"}
            try:
                response = get(cloud_url, headers=headers, timeout=10)
                status_code = response.status_code
            except:
                pass
        if status_code == 200:
            self._state = new_state
            self.schedule_update_ha_state()
        else:
            _LOGGER.error("action error : "+str(status_code))
            raise Exception("action error : "+str(status_code)) 
