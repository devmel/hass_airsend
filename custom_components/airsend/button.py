"""AirSend buttons."""
from typing import Any

from .device import Device

from homeassistant.components.button import ButtonEntity
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
    """Set up AirSend buttons from a config entry."""
    internal_url = entry.data.get(CONF_INTERNAL_URL, "")
    devices_config = entry.data.get("devices", {})

    entities = []
    for name, options in devices_config.items():
        device = Device(name, options, internal_url)
        if device.is_button:
            entities.append(AirSendButton(hass, device))

    async_add_entities(entities)


class AirSendButton(ButtonEntity):
    """Representation of an AirSend Button."""

    def __init__(self, hass: HomeAssistant, device: Device) -> None:
        self._device = device
        self._unique_id = DOMAIN + "_" + str(device.unique_channel_name) + "_button"

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
        return None

    @property
    def assumed_state(self):
        return True

    @property
    def device_info(self) -> DeviceInfo:
        return self._device.device_info

    def press(self, **kwargs: Any) -> None:
        note = {"method": 1, "type": 0, "value": "TOGGLE"}
        if self._device.transfer(note, self.entity_id):
            self.schedule_update_ha_state()
