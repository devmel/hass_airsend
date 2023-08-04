"""AirSend switches."""
from typing import Any

from .device import Device

from homeassistant.components.switch import SwitchEntity
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
        if device.is_switch:
            entity = AirSendSwitch(
                hass,
                device,
            )
            async_add_entities([entity])


class AirSendSwitch(SwitchEntity):
    """Representation of an AirSend Switch."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: Device,
    ) -> None:
        """Initialize a switch or light device."""
        self._device = device
        uname = DOMAIN + device.name
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
    def is_on(self):
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        note = {"method": 1, "type": 0, "value": "ON"}
        if self._device.transfer(note, self.entity_id) == True:
            self._state = True
            self.schedule_update_ha_state()

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        note = {"method": 1, "type": 0, "value": "OFF"}
        if self._device.transfer(note, self.entity_id) == True:
            self._state = False
            self.schedule_update_ha_state()
