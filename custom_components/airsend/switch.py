"""AirSend switches."""
from typing import Any

from .device import Device

from homeassistant.components.switch import SwitchEntity
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
    """Set up AirSend switches from a config entry."""
    internal_url = entry.data.get(CONF_INTERNAL_URL, "")
    devices_config = entry.data.get("devices", {})

    entities = []
    for name, options in devices_config.items():
        device = Device(name, options, internal_url)
        if device.is_switch:
            entities.append(AirSendSwitch(hass, device))

    async_add_entities(entities)


class AirSendSwitch(SwitchEntity):
    """Representation of an AirSend Switch."""

    def __init__(self, hass: HomeAssistant, device: Device) -> None:
        self._hass = hass
        self._device = device
        self._unique_id = DOMAIN + "_" + str(device.unique_channel_name) + "_switch"
        self._state = None

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def available(self):
        return True

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
    def is_on(self):
        if self._device.is_async and self._hass:
            component = self._hass.states.get(self.entity_id)
            if component is not None:
                self._state = component.state == 'on'
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        note = {"method": 1, "type": 0, "value": "ON"}
        if self._device.transfer(note, self.entity_id):
            self._state = True
            self.schedule_update_ha_state()

    def turn_off(self, **kwargs: Any) -> None:
        note = {"method": 1, "type": 0, "value": "OFF"}
        if self._device.transfer(note, self.entity_id):
            self._state = False
            self.schedule_update_ha_state()
