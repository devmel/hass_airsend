"""AirSend lights (dimmable)."""
from typing import Any

from .device import Device, TransferResult

from homeassistant.components.light import LightEntity, ATTR_BRIGHTNESS, ColorMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.const import CONF_INTERNAL_URL

from . import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AirSend lights from a config entry."""
    internal_url = entry.data.get(CONF_INTERNAL_URL, "")
    devices_config = entry.data.get("devices", {})
    entities = []
    for name, options in devices_config.items():
        device = Device(name, options, internal_url)
        if device.is_light:
            entities.append(AirSendLight(hass, device))
    async_add_entities(entities)


class AirSendLight(RestoreEntity, LightEntity):
    """Representation of an AirSend dimmable light."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(self, hass: HomeAssistant, device: Device) -> None:
        self._hass = hass
        self._device = device
        self._unique_id = DOMAIN + "_" + str(device.unique_channel_name) + "_light"
        self._available = True
        self._is_on = False
        self._brightness = 255

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._device.name

    @property
    def available(self):
        return self._available

    @property
    def should_poll(self):
        return False

    @property
    def assumed_state(self):
        return True

    @property
    def device_info(self) -> DeviceInfo:
        return self._device.device_info

    @property
    def is_on(self) -> bool:
        return self._is_on

    @property
    def brightness(self) -> int:
        return self._brightness

    async def async_added_to_hass(self):
        """Restore last known state when added to hass."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in ('unavailable', 'unknown'):
            self._is_on = last_state.state == 'on'
            if last_state.attributes.get('brightness') is not None:
                self._brightness = last_state.attributes['brightness']
        self.async_write_ha_state()

    async def _send(self, note: dict) -> bool:
        """Send command and update availability."""
        result = await self._device.async_transfer(note, self.entity_id)
        available = result != TransferResult.NETWORK_ERROR
        if self._available != available:
            self._available = available
            self.async_write_ha_state()
        return result in (TransferResult.SUCCESS, TransferResult.SENT)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on or dim the light."""
        if ATTR_BRIGHTNESS in kwargs:
            level = max(1, round(kwargs[ATTR_BRIGHTNESS] / 255 * 100))
            note = {"method": 1, "type": 9, "value": level}
            if await self._send(note):
                self._brightness = kwargs[ATTR_BRIGHTNESS]
                self._is_on = True
                self.async_write_ha_state()
        else:
            level = max(1, round(self._brightness / 255 * 100))
            note = {"method": 1, "type": 9, "value": level}
            if await self._send(note):
                self._is_on = True
                self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        note = {"method": 1, "type": 0, "value": "OFF"}
        if await self._send(note):
            self._is_on = False
            self.async_write_ha_state()
