"""AirSend binary sensors — state monitoring for AirSend boxes (type 0)."""
from datetime import timedelta
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_INTERNAL_URL

from .device import Device
from . import DOMAIN

_LOGGER = logging.getLogger(DOMAIN)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AirSend binary sensors from a config entry."""
    internal_url = entry.data.get(CONF_INTERNAL_URL, "")
    devices_config = entry.data.get("devices", {})

    entities = []
    for name, options in devices_config.items():
        device = Device(name, options, internal_url)
        if device.is_airsend:
            entities.append(AirSendStateSensor(hass, device))

    async_add_entities(entities)


class AirSendStateSensor(BinarySensorEntity):
    """Binary sensor representing the running state of an AirSend box."""

    def __init__(self, hass: HomeAssistant, device: Device) -> None:
        self.hass = hass
        self._device = device
        uname = DOMAIN + "_" + str(device.unique_channel_name) + "_state"
        self._unique_id = uname
        self._coordinator = DataUpdateCoordinator(
            hass, _LOGGER,
            name=uname,
            update_method=self.async_update_data,
            update_interval=timedelta(seconds=10),
        )
        self._coordinator.async_add_listener(lambda: None)

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._device.name + "_state"

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        return BinarySensorDeviceClass.RUNNING

    @property
    def available(self):
        return True

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def device_info(self) -> DeviceInfo:
        return self._device.device_info

    async def async_update_data(self):
        self._coordinator.update_interval = timedelta(seconds=self._device.refresh_value)
        note = {"method": "QUERY", "type": "STATE"}
        await self.hass.async_add_executor_job(
            lambda: self._device.transfer(note, self.entity_id)
        )
        await self.hass.async_add_executor_job(
            lambda: self._device.bind()
        )
