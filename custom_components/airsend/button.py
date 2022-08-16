"""AirSend buttons."""
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
from homeassistant.components.button import (
    ButtonEntity,
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
        if options['type'] == 4096 :
            id = ""
            apiKey = ""
            spurl = ""
            channel = {}
            note = {"method":1,"type":0,"value": "TOGGLE"}
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
            try:
                note = options['note']
            except KeyError:
                pass
            entity = AirSendButton(hass, name, id, options['type'], apiKey, addons_url, spurl, channel, note)
            async_add_entities([entity])
    return


class AirSendButton(ButtonEntity):
    """Representation of an AirSend Button."""

    def __init__(self, hass : HomeAssistant, name : str, id: str, type : int, apikey : str, addons_url : str, spurl : str, channel : dict, note : dict):
        """Initialize a button."""
        self._name = name
        self._id = id
        self._type = type
        self._apikey = apikey
        self._addons_url = addons_url
        self._spurl = spurl
        self._channel = channel
        self._note = note
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

    def press(self) -> None:
        """Handle the button press."""
        command = "6"
        note = self._note
        url = "https://airsend.cloud/device/" + str(self._id) + "/command/" + command + "/"
        payload = '{"wait": true, "channel":' + json.dumps(self._channel) + ', "thingnotes":{"notes":[' + json.dumps(
            note) + ']}}'
        self._action(url, payload, True)

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
