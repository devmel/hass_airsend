"""AirSend covers."""
from typing import Any

from .device import TransferResult
from .coordinator import AirSendCoordinator

from homeassistant.components.cover import CoverEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AirSend covers from a config entry."""
    coordinators: dict[str, AirSendCoordinator] = (
        hass.data[DOMAIN][entry.entry_id]["coordinators"]
    )
    entities = []
    for coordinator in coordinators.values():
        if coordinator.device.is_cover:
            entities.append(AirSendCover(hass, coordinator))
    async_add_entities(entities)


class AirSendCover(CoordinatorEntity, RestoreEntity, CoverEntity):
    """Representation of an AirSend Cover."""

    def __init__(self, hass: HomeAssistant, coordinator: AirSendCoordinator) -> None:
        super().__init__(coordinator)
        self._hass = hass
        self._device = coordinator.device
        self._unique_id = DOMAIN + "_" + str(coordinator.device.unique_channel_name) + "_cover"
        self._closed = None
        if coordinator.device.is_cover_with_position:
            self._attr_current_cover_position = 50

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def available(self):
        return self.coordinator.data.get("available", True)

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return self._device.name

    @property
    def extra_state_attributes(self):
        attrs = self._device.extra_state_attributes or {}
        if self._device.is_inverted:
            attrs = {**attrs, "inverted": True}
        return attrs or None

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
                is_open_state = component.state not in ('open', 'on', 'up')
                # Invert the closed logic if needed
                self._closed = not is_open_state if self._device.is_inverted else is_open_state
        return self._closed

    async def async_added_to_hass(self):
        """Restore last known state when added to hass."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in ('unavailable', 'unknown'):
            if self._device.is_cover_with_position:
                if last_state.attributes.get('current_position') is not None:
                    self._attr_current_cover_position = last_state.attributes['current_position']
                if last_state.state == 'closed':
                    self._attr_current_cover_position = 0
                elif last_state.state == 'open':
                    self._attr_current_cover_position = 100
            if last_state.state == 'closed':
                self._closed = True
            elif last_state.state == 'open':
                self._closed = False
        self.async_write_ha_state()
        # Validate reachability right after startup (bridge may still be
        # coming up after a host/VM restart) instead of waiting one interval
        await self.coordinator.async_request_refresh()

    async def _send(self, note: dict) -> bool:
        """Send a command and update availability accordingly."""
        result = await self._device.async_transfer(note, self.entity_id)
        available = result != TransferResult.NETWORK_ERROR
        if available != self.coordinator.data.get("available", True):
            self.coordinator.async_set_available(available)
        if not available:
            # Confirm reachability right away instead of waiting for the next probe
            await self.coordinator.async_request_refresh()
        return result in (TransferResult.SUCCESS, TransferResult.SENT)

    def _up_note(self) -> dict:
        """Return UP note, inverted if needed."""
        value = "DOWN" if self._device.is_inverted else "UP"
        return {"method": 1, "type": 0, "value": value}

    def _down_note(self) -> dict:
        """Return DOWN note, inverted if needed."""
        value = "UP" if self._device.is_inverted else "DOWN"
        return {"method": 1, "type": 0, "value": value}

    async def async_open_cover(self, **kwargs: Any) -> None:
        if await self._send(self._up_note()):
            self._closed = False
            if self._device.is_cover_with_position:
                self._attr_current_cover_position = 100
            self.async_write_ha_state()

    async def async_close_cover(self, **kwargs: Any) -> None:
        if await self._send(self._down_note()):
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
        # Invert position value if needed
        actual_position = (100 - position) if self._device.is_inverted else position
        note = {"method": 1, "type": 9, "value": actual_position}
        if await self._send(note):
            self._attr_current_cover_position = position
            self._closed = position == 0
            self.async_write_ha_state()
