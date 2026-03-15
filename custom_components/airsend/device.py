"""AirSend device."""
import logging
import json
import hashlib
import aiohttp
from . import DOMAIN

_LOGGER = logging.getLogger(DOMAIN)

RTYPE_LABELS = {
    0: "AirSend",
    1: "AirSend Sensor",
    4096: "AirSend Button",
    4097: "AirSend Switch",
    4098: "AirSend Cover",
    4099: "AirSend Cover (position)",
}


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
        self._bind = None
        self._refresh = 5 * 60
        try:
            self._uid = options["id"]
        except KeyError:
            pass
        try:
            self._rtype = options["type"]
        except KeyError:
            pass
        if self._rtype == 0:
            self._channel = {"id": 1}
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
        try:
            self._bind = int(options["bind"])
        except KeyError:
            pass
        try:
            self._refresh = int(options["refresh"])
        except KeyError:
            pass

    @property
    def name(self) -> str:
        """Return the name."""
        return self._name

    @property
    def unique_channel_name(self) -> str:
        if self._uid:
            return str(self._uid)
        if self._channel:
            result = str(self._channel['id'])
            if result:
                uniquefield = ['source', 'mac', 'seed']
                for field in uniquefield:
                    if field in self._channel:
                        result += "_"
                        result += str(self._channel[field])
            return result
        return self._name

    @property
    def device_info(self) -> dict:
        """Return device info for Home Assistant device registry."""
        return {
            "identifiers": {(DOMAIN, self.unique_channel_name)},
            "name": self._name,
            "manufacturer": "AirSend",
            "model": RTYPE_LABELS.get(self._rtype, "AirSend"),
        }

    @property
    def extra_state_attributes(self):
        if self._channel:
            return {"channel": self._channel}
        return None

    @property
    def is_async(self) -> bool:
        """Return if asynchronous state."""
        return self._wait == False

    @property
    def is_airsend(self) -> bool:
        return self._rtype == 0

    @property
    def is_sensor(self) -> bool:
        return self._rtype == 1

    @property
    def is_button(self) -> bool:
        return self._rtype == 4096

    @property
    def is_cover(self) -> bool:
        return self._rtype in (4098, 4099)

    @property
    def is_cover_with_position(self) -> bool:
        return self._rtype == 4099

    @property
    def is_switch(self) -> bool:
        return self._rtype == 4097

    @property
    def refresh_value(self) -> int:
        """Return refresh value in seconds."""
        if isinstance(self._refresh, int) and self._refresh > 0:
            return self._refresh
        return 5 * 60

    async def async_bind(self) -> bool:
        """Bind a channel to listen (async)."""
        if not (self._serviceurl and self._spurl and isinstance(self._bind, int) and self._bind > 0):
            return False
        payload = json.dumps({
            "channel": {"id": self._bind},
            "duration": 0,
            "callback": "http://127.0.0.1/"
        })
        headers = {
            "Authorization": "Bearer " + self._spurl,
            "content-type": "application/json",
            "User-Agent": "hass_airsend",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self._serviceurl + "airsend/bind",
                    headers=headers,
                    data=payload,
                    timeout=aiohttp.ClientTimeout(total=6),
                ) as response:
                    return response.status == 200
        except aiohttp.ClientError as err:
            _LOGGER.debug("Bind error '%s': %s", self._name, err)
            return False

    async def async_transfer(self, note, entity_id=None) -> bool:
        """Send a command (async)."""
        status_code = 404
        ret = False
        wait = 'false, "callback":"http://127.0.0.1/"'
        if self._wait:
            wait = 'true'

        if self._serviceurl and self._spurl and entity_id is not None:
            uid = hashlib.sha256(entity_id.encode('utf-8')).hexdigest()[:12]
            jnote = json.dumps(note)
            if (
                self._note is not None
                and all(k in self._note for k in ("method", "type", "value"))
                and all(k in note for k in ("method", "type", "value"))
                and note["method"] == 1 and note["type"] == 0
                and note["value"] in ("TOGGLE", 6)
            ):
                jnote = json.dumps(self._note)

            payload = (
                '{"wait": ' + wait + ', "channel":'
                + json.dumps(self._channel)
                + ', "thingnotes":{"uid":"0x' + uid + '", "notes":['
                + jnote
                + "]}}"
            )
            headers = {
                "Authorization": "Bearer " + self._spurl,
                "content-type": "application/json",
                "User-Agent": "hass_airsend",
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self._serviceurl + "airsend/transfer",
                        headers=headers,
                        data=payload,
                        timeout=aiohttp.ClientTimeout(total=6),
                    ) as response:
                        if self._wait:
                            ret = True
                            status_code = 500
                            try:
                                jdata = await response.json(content_type=None)
                                if jdata.get("type", 0x100) < 0x100:
                                    status_code = response.status
                            except Exception:
                                pass
                        else:
                            ret = None
                            status_code = response.status
            except aiohttp.ClientError as err:
                _LOGGER.debug("Transfer local error '%s': %s", self._name, err)

        # Fallback to cloud API if local failed
        if status_code != 200 and self._apikey:
            action = "command"
            value = 6
            if all(k in note for k in ("method", "type", "value")):
                if note["method"] == 1 and note["type"] == 0:
                    value = {
                        "OFF": 0, "ON": 1, "STOP": 3, "DOWN": 4, "UP": 5
                    }.get(note["value"], 6)
                elif note["method"] == 1 and note["type"] == 9:
                    action = "level"
                    value = int(note["value"])

            cloud_url = (
                "https://airsend.cloud/device/"
                + str(self._uid) + "/" + action + "/" + str(value) + "/"
            )
            headers = {
                "Authorization": "Bearer " + self._apikey,
                "content-type": "application/json",
                "User-Agent": "hass_airsend",
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        cloud_url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as response:
                        status_code = response.status
                        ret = True
            except aiohttp.ClientError as err:
                _LOGGER.debug("Transfer cloud error '%s': %s", self._name, err)

        if status_code == 200:
            return ret
        _LOGGER.error("Transfer error '%s' : '%s'", self.name, status_code)
        return False
