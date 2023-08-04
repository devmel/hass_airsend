"""AirSend device."""
import logging
import json
import hashlib
from requests import get, post, exceptions
from . import DOMAIN

_LOGGER = logging.getLogger(DOMAIN)


class Device:
    """Representation of a Device."""

    def __init__(
        self,
        name: str,
        options,
        serviceurl: str,
    ) -> None:
        """Initialize a device."""
        self._name = name
        self._serviceurl = serviceurl
        self._uid = None
        self._rtype = None
        self._apikey = None
        self._spurl = None
        self._wait = False
        self._channel = {}
        self._note = None
        try:
            self._uid = options["id"]
        except KeyError:
            pass
        try:
            self._rtype = options["type"]
        except KeyError:
            pass
        try:
            self._apikey = options["apiKey"]
        except KeyError:
            pass
        try:
            self._spurl = options["spurl"]
        except KeyError:
            pass
        try:
            self._wait = eval(str(options["wait"]))
        except KeyError:
            pass
        try:
            self._channel = options["channel"]
        except KeyError:
            pass
        try:
            self._note = options["note"]
        except KeyError:
            pass

    @property
    def name(self) -> str:
        """Return the name."""
        return self._name

    @property
    def is_button(self) -> bool:
        """Return if is a button."""
        if self._rtype == 4096:
            return True
        return False

    @property
    def is_cover(self) -> bool:
        """Return if is a cover."""
        if self._rtype in (4098, 4099):
            return True
        return False

    @property
    def is_cover_with_position(self) -> bool:
        """Return if is a cover with position."""
        if self._rtype == 4099:
            return True
        return False

    @property
    def is_switch(self) -> bool:
        """Return if is a switch."""
        if self._rtype == 4097:
            return True
        return False

    def transfer(self, note, entity_id = None) -> bool:
        """Send a command."""
        status_code = 404
        ret = False
        wait = 'false, "callback":"http://127.0.0.1/"'
        if self._wait == True:
            wait = 'true'
        if self._serviceurl and self._spurl and entity_id is not None:
            uid = hashlib.sha256(entity_id.encode('utf-8')).hexdigest()[:12]
            jnote = json.dumps(note)
            if (
                self._note is not None
                and "method" in self._note
                and "type" in self._note
                and "value" in self._note
                and "method" in note.keys()
                and "type" in note.keys()
                and "value" in note.keys()
                and note["method"] == 1 and note["type"] == 0
                and (note["value"] == "TOGGLE" or note["value"] == 6)
            ):
                jnote = json.dumps(self._note)
            payload = (
                '{"wait": '+wait+', "channel":'
                + json.dumps(self._channel)
                + ', "thingnotes":{"uid":"0x'+uid+'", "notes":['
                + jnote
                + "]}}"
            )
            headers = {
                "Authorization": "Bearer " + self._spurl,
                "content-type": "application/json",
                "User-Agent": "hass_airsend",
            }
            try:
                response = post(
                    self._serviceurl + "airsend/transfer",
                    headers=headers,
                    data=payload,
                    timeout=6,
                )
                if self._wait == True:
                    ret = True
                    status_code = 500
                    jdata = json.loads(response.text)
                    if jdata["type"] < 0x100:
                        status_code = response.status_code
                else:
                    ret = None
                    status_code = response.status_code
            except exceptions.RequestException:
                pass
        if status_code != 200 and self._apikey:
            action = "command"
            value = 6
            if (
                "method" in note.keys()
                and "type" in note.keys()
                and "value" in note.keys()
            ):
                if note["method"] == 1 and note["type"] == 0:
                    if note["value"] == "OFF":
                        value = 0
                    if note["value"] == "ON":
                        value = 1
                    if note["value"] == "STOP":
                        value = 3
                    if note["value"] == "DOWN":
                        value = 4
                    if note["value"] == "UP":
                        value = 5
                if note["method"] == 1 and note["type"] == 9:
                    action = "level"
                    value = int(note["value"])
            cloud_url = (
                "https://airsend.cloud/device/"
                + str(self._uid)
                + "/"
                + action
                + "/"
                + str(value)
                + "/"
            )
            headers = {
                "Authorization": "Bearer " + self._apikey,
                "content-type": "application/json",
                "User-Agent": "hass_airsend",
            }
            try:
                response = get(cloud_url, headers=headers, timeout=10)
                status_code = response.status_code
                ret = True
            except exceptions.RequestException:
                pass
        if status_code == 200:
            return ret
        _LOGGER.error("Transfer error '%s' : '%s'", self.name, status_code)
        raise Exception("Transfer error " + self.name + " : " + str(status_code))
