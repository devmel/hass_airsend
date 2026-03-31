"""AirSend covers."""
from typing import Any

from .device import Device

from homeassistant.components.cover import CoverEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import CONF_INTERNAL_URL

from . import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AirSend covers from a config entry."""
    internal_url = entry.data.get(CONF_INTERNAL_URL, "")
    devices_config = entry.data.get("devices", {})
    entities = []
    for name, options in devices_config.items():
        device = Device(name, options, internal_url)
        if device.is_cover:
            entities.append(AirSendCover(hass, device))
    async_add_entities(entities)


class AirSendCover(CoverEntity):
    """Representation of an AirSend Cover."""

    def __init__(self, hass: HomeAssistant, device: Device) -> None:
        self._hass = hass
        self._device = device
        self._unique_id = DOMAIN + "_" + str(device.unique_channel_name) + "_cover"
        self._closed = None
        self._available = True
        if device.is_cover_with_position:
            self._attr_current_cover_position = 50

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def available(self):
        return self._available

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return self._device.name

    @property
    def extra_state_attributes(self):
        return self._device.extra_state_attributes

    @property
    def assumed_state(self):
        return True

    @property
    def device_info(self) -> DeviceInfo:
        return self._device.device_info

    @property
    def is_closed(self):
        if self._device.is_async and self._hass:
            component = self._hass.states.get(self.entity_id)
            if component is not None:
                self._closed = component.state not in ('open', 'on', 'up')
        return self._closed

    async def _send(self, note: dict) -> bool:
        """Send a command and update availability accordingly."""
        result = await self._device.async_transfer(note, self.entity_id)
        available = result is not False
        if self._available != available:
            self._available = available
            self.async_write_ha_state()
        return result is not False

    async def async_open_cover(self, **kwargs: Any) -> None:
        note = {"method": 1, "type": 0, "value": "UP"}
        if await self._send(note):
            self._closed = False
            if self._device.is_cover_with_position:
                self._attr_current_cover_position = 100
            self.async_write_ha_state()

    async def async_close_cover(self, **kwargs: Any) -> None:
        note = {"method": 1, "type": 0, "value": "DOWN"}
        if await self._send(note):
            self._closed = True
            if self._device.is_cover_with_position:
                self._attr_current_cover_position = 0
            self.async_write_ha_state()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        note = {"method": 1, "type": 0, "value": "STOP"}
        if await self._send(note):
            self._closed = False
            if self._device.is_cover_with_position:
                self._attr_current_cover_position = 50
            self.async_write_ha_state()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        position = int(kwargs["position"])
        note = {"method": 1, "type": 9, "value": position}
        if await self._send(note):
            self._attr_current_cover_position = position
            self._closed = position == 0
            self.async_write_ha_state()
