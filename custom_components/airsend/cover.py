"""AirSend switches."""
from typing import Any

from .device import Device

from homeassistant.components.cover import CoverEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from homeassistant.const import CONF_DEVICES, CONF_INTERNAL_URL

from . import DOMAIN


async def async_setup_platform(
    hass: HomeAssistant, config: ConfigType, async_add_entities, discovery_info=None
) -> None:
    if discovery_info is None:
        return
    for name, options in discovery_info[CONF_DEVICES].items():
        device = Device(name, options, discovery_info[CONF_INTERNAL_URL])
        if device.is_cover:
            entity = AirSendCover(
                hass,
                device,
            )
            async_add_entities([entity])


class AirSendCover(CoverEntity):
    """Representation of an AirSend Cover."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: Device,
    ) -> None:
        """Initialize a cover device."""
        self._device = device
        uname = DOMAIN + device.name
        self._unique_id = "_".join(x for x in uname)
        self._closed = False
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
        """Return the device state attributes."""
        return None

    @property
    def assumed_state(self):
        """Return true if unable to access real state of entity."""
        return True

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return not self._closed

    def open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        note = {"method": 1, "type": 0, "value": "UP"}
        if self._device.transfer(note):
            self._closed = False
            if self._device.is_cover_with_position:
                self._attr_current_cover_position = 100
            self.schedule_update_ha_state()

    def close_cover(self, **kwargs: Any) -> None:
        """Close cover."""
        note = {"method": 1, "type": 0, "value": "DOWN"}
        if self._device.transfer(note):
            self._closed = True
            if self._device.is_cover_with_position:
                self._attr_current_cover_position = 0
            self.schedule_update_ha_state()

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        note = {"method": 1, "type": 0, "value": "STOP"}
        if self._device.transfer(note):
            self._closed = False
            if self._device.is_cover_with_position:
                self._attr_current_cover_position = 50
            self.schedule_update_ha_state()

    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = int(kwargs["position"])
        note = {"method": 1, "type": 9, "value": position}
        if self._device.transfer(note):
            self._attr_current_cover_position = position
            self._closed = False
            if self._attr_current_cover_position == 0:
                self._closed = True
            self.schedule_update_ha_state()
