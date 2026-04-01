"""AirSend sensors."""
import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_INTERNAL_URL, UnitOfTemperature, LIGHT_LUX

from .coordinator import AirSendCoordinator
from .device import Device
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
    devices_config = entry.data.get("devices", {})
    internal_url = entry.data.get(CONF_INTERNAL_URL, "")

    entities = []
    for name, coordinator in coordinators.items():
        device = coordinator.device
        options = devices_config.get(name, {})

        # Generic external sensor (type 1) — no coordinator needed
        if device.is_sensor:
            entities.append(AirSendAnySensor(hass, device, internal_url))

        # AirSend box sensors (type 0)
        if device.is_airsend:
            sensors = False
            try:
                sensors = eval(str(options.get("sensors", False)))
            except Exception:
                pass
            if sensors:
                coordinator.set_has_sensors(True)
                entities.append(AirSendTempSensor(coordinator))
                entities.append(AirSendIllSensor(coordinator))

    async_add_entities(entities)


class AirSendAnySensor(RestoreEntity, SensorEntity):
    """Generic AirSend sensor (type 1) — no coordinator, push only."""

    def __init__(self, hass: HomeAssistant, device: Device, internal_url: str) -> None:
        self._device = device
        self._unique_id = DOMAIN + "_" + str(device.unique_channel_name) + "_sensor"
        self.entity_id = generate_entity_id("sensor.{}", device.unique_channel_name, hass=hass)

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._device.name

    @property
    def extra_state_attributes(self):
        return self._device.extra_state_attributes

    @property
    def available(self):
        return True

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def device_info(self) -> DeviceInfo:
        return self._device.device_info

    @property
    def native_value(self):
        return self._state

    async def async_added_to_hass(self) -> None:
        """Restore last known state when added to hass."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._state = last_state.state
            self.async_write_ha_state()


class AirSendTempSensor(CoordinatorEntity, SensorEntity):
    """AirSend device temperature sensor — uses shared coordinator."""

    def __init__(self, coordinator: AirSendCoordinator) -> None:
        super().__init__(coordinator)
        self._unique_id = DOMAIN + "_" + str(coordinator.device.unique_channel_name) + "_temp"

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self.coordinator.device.name + "_temp"

    @property
    def available(self) -> bool:
        return self.coordinator.data.get("available", True)

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.TEMPERATURE

    @property
    def native_unit_of_measurement(self):
        return UnitOfTemperature.CELSIUS

    @property
    def native_value(self):
        return self.coordinator.data.get("temperature")

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device.device_info


class AirSendIllSensor(CoordinatorEntity, SensorEntity):
    """AirSend device illuminance sensor — uses shared coordinator."""

    def __init__(self, coordinator: AirSendCoordinator) -> None:
        super().__init__(coordinator)
        self._unique_id = DOMAIN + "_" + str(coordinator.device.unique_channel_name) + "_ill"

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self.coordinator.device.name + "_ill"

    @property
    def available(self) -> bool:
        return self.coordinator.data.get("available", True)

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.ILLUMINANCE

    @property
    def native_unit_of_measurement(self):
        return LIGHT_LUX

    @property
    def native_value(self):
        return self.coordinator.data.get("illuminance")

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device.device_info
