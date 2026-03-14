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
    data = entry.data
    internal_url = data.get(CONF_INTERNAL_URL, "")
    devices_config = data.get("devices", {})

    entities = []
    for name, options in devices_config.items():
        device = Device(name, options, internal_url)
        if device.is_cover:
            entities.append(AirSendCover(hass, device))

    async_add_entities(entities)


class AirSendCover(CoverEntity):
    """Representation of an AirSend Cover."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: Device,
    ) -> None:
        """Initialize a cover device."""
        self._hass = hass
        self._device = device
        self._unique_id = DOMAIN + "_" + device.unique_channel_name + "_cover"
        self._closed = None
        if device.is_cover_with_position:
            self._attr_current_cover_position = 50

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
        return self._device.name

    @property
    def extra_state_attributes(self):
        return self._device.extra_state_attributes

    @property
    def assumed_state(self):
        """Return true if unable to access real state of entity."""
        return True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info to link this entity to a device."""
        return self._device.device_info

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        if self._device.is_async and self._hass:
            component = self._hass.states.get(self.entity_id)
            if component is not None:
                self._closed = component.state not in ('open', 'on', 'up')
        return self._closed

    def open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        note = {"method": 1, "type": 0, "value": "UP"}
        if self._device.transfer(note, self.entity_id):
            self._closed = False
            if self._device.is_cover_with_position:
                self._attr_current_cover_position = 100
            self.schedule_update_ha_state()

    def close_cover(self, **kwargs: Any) -> None:
        """Close cover."""
        note = {"method": 1, "type": 0, "value": "DOWN"}
        if self._device.transfer(note, self.entity_id):
            self._closed = True
            if self._device.is_cover_with_position:
                self._attr_current_cover_position = 0
            self.schedule_update_ha_state()

    def stop_cover(self, **kwargs) -> None:
        """Stop the cover."""
        note = {"method": 1, "type": 0, "value": "STOP"}
        if self._device.transfer(note, self.entity_id):
            self._closed = False
            if self._device.is_cover_with_position:
                self._attr_current_cover_position = 50
            self.schedule_update_ha_state()

    def set_cover_position(self, **kwargs) -> None:
        """Move the cover to a specific position."""
        position = int(kwargs["position"])
        note = {"method": 1, "type": 9, "value": position}
        if self._device.transfer(note, self.entity_id):
            self._attr_current_cover_position = position
            self._closed = position == 0
            self.schedule_update_ha_state()
