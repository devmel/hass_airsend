"""AirSend binary sensors — state monitoring for AirSend boxes (type 0)."""
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AirSendCoordinator
from . import DOMAIN

_LOGGER = logging.getLogger(DOMAIN)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators: dict[str, AirSendCoordinator] = (
        hass.data[DOMAIN][entry.entry_id]["coordinators"]
    )
    entities = []
    for name, coordinator in coordinators.items():
        if coordinator.device.is_airsend:
            entities.append(AirSendStateSensor(coordinator))
    async_add_entities(entities)


class AirSendStateSensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor representing the running state of an AirSend box."""

    def __init__(self, coordinator: AirSendCoordinator) -> None:
        super().__init__(coordinator)
        self._unique_id = DOMAIN + "_" + str(coordinator.device.unique_channel_name) + "_state"

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self.coordinator.device.name + "_state"

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        return BinarySensorDeviceClass.RUNNING

    @property
    def available(self) -> bool:
        return self.coordinator.data.get("available", True)

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get("available", True)

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device.device_info
